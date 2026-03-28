"""
Certificate image and PDF generation pipeline using Pillow.

This module renders professional certificates as A4 landscape images (2339x1654 px at
200 DPI), then converts them to PDF. The pipeline is: create blank canvas -> draw
decorative borders -> place watermark and logo -> render text (org name, recipient,
body, signature) -> embed QR code -> save as PNG and PDF.

I chose Pillow over a template-based approach (e.g., WeasyPrint or ReportLab) because
we need pixel-precise control over the certificate layout, including custom fonts
(Great Vibes for signatures), decorative corner ornaments, and a semi-transparent
watermark. Template engines don't give us this level of control.

The tasks run via Celery so the HTTP request returns immediately while generation
happens in the background. In dev mode (CELERY_TASK_ALWAYS_EAGER=True), they run
synchronously.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import io
import logging
import os
import platform
import re
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

logger = logging.getLogger("apps.certificates")

# Colors
NAVY = (0, 51, 102)
RED = (187, 0, 0)
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
CREAM = (253, 251, 247)
GOLD = (185, 155, 60)
GOLD_LIGHT = (215, 195, 120)
GRAY = (110, 110, 110)
BODY_COLOR = (60, 60, 60)

# A4 landscape at 200 DPI (fast generation, still print-quality)
W = 2339
H = 1654

FONTS_DIR = Path(settings.BASE_DIR) / "static" / "fonts"
LOGO_PATHS = [
    Path(settings.BASE_DIR) / "static" / "images" / "kck-logo.png",
    Path(settings.BASE_DIR).parent / "frontend" / "public" / "images" / "kck-logo.png",
]


def _get_font_path(font_name="DejaVuSans.ttf"):
    """
    Find a font file cross-platform.

    Font loading is one of the trickiest parts of server-side image generation. We need
    to support three environments: Windows dev machines (where fonts live in C:\\Windows\\Fonts),
    macOS dev machines (/Library/Fonts), and Linux production servers (/usr/share/fonts).
    We check bundled fonts first (shipped with the project in static/fonts/) so that
    production deployments are self-contained and don't depend on system font availability.
    """
    bundled = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'fonts', font_name)
    if os.path.exists(bundled):
        return bundled

    font_dirs = []
    system = platform.system()
    if system == "Windows":
        font_dirs.append(os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"))
    elif system == "Darwin":  # macOS
        font_dirs.extend(["/Library/Fonts", os.path.expanduser("~/Library/Fonts"), "/System/Library/Fonts"])
    else:  # Linux
        font_dirs.extend([
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts",
            "/usr/local/share/fonts",
        ])

    for font_dir in font_dirs:
        path = os.path.join(font_dir, font_name)
        if os.path.exists(path):
            return path

    return None  # Will use Pillow default


def _font(size, bold=False, script=False):
    from PIL import ImageFont

    if script:
        # Great Vibes for signature-style text
        gv = FONTS_DIR / "GreatVibes-Regular.ttf"
        if gv.exists():
            try:
                return ImageFont.truetype(str(gv), size)
            except:
                pass

    # Cross-platform font names: prefer DejaVu (available on Linux), fall back to Arial (Windows)
    if bold:
        font_names = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "ArialBD.ttf"]
    else:
        font_names = ["DejaVuSans.ttf", "arial.ttf", "Arial.ttf"]

    for name in font_names:
        path = _get_font_path(name)
        if path:
            try:
                return ImageFont.truetype(path, size)
            except:
                pass

    # Last resort: try by name (system font lookup)
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except:
            pass

    return ImageFont.load_default()


def _tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def _center(draw, text, y, font, fill):
    w, _ = _tw(draw, text, font)
    draw.text(((W - w) // 2, y), text, fill=fill, font=font)
    return w


def _center_at(draw, text, y, cx, font, fill):
    w, _ = _tw(draw, text, font)
    draw.text((cx - w // 2, y), text, fill=fill, font=font)


def _wrap(text, font, max_w):
    from PIL import ImageDraw, Image as _I
    d = ImageDraw.Draw(_I.new("RGB", (1, 1)))
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        bb = d.textbbox((0, 0), t, font=font)
        if bb[2] - bb[0] <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _load_logo():
    from PIL import Image
    for p in LOGO_PATHS:
        if p.exists():
            try:
                return Image.open(p).convert("RGBA")
            except:
                pass
    return None


def _placeholder_logo(size=200):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, size - 4, size - 4], outline=NAVY, width=5)
    f = _font(size // 3, bold=True)
    w, h = _tw(d, "KCK", f)
    d.text(((size - w) // 2, (size - h) // 2), "KCK", fill=NAVY, font=f)
    return img


@shared_task
def generate_cert_image_task(certificate_id):
    """Generate professional certificate PNG + PDF."""
    from .models import Certificate

    try:
        cert = Certificate.objects.select_related("issued_by__user").get(id=certificate_id)
    except Certificate.DoesNotExist:
        logger.error(f"[CERT] Not found: {certificate_id}")
        return

    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (W, H), CREAM)
        draw = ImageDraw.Draw(img)

        # ============================================================
        # DECORATIVE BORDER
        # ============================================================
        # Outer gold border
        draw.rectangle([40, 40, W - 40, H - 40], outline=GOLD, width=6)
        # Inner navy border
        draw.rectangle([60, 60, W - 60, H - 60], outline=NAVY, width=3)
        # Innermost thin gold line
        draw.rectangle([70, 70, W - 70, H - 70], outline=GOLD_LIGHT, width=1)

        # Corner ornaments
        for cx, cy, dx, dy in [(80, 80, 1, 1), (W-80, 80, -1, 1),
                                (80, H-80, 1, -1), (W-80, H-80, -1, -1)]:
            for i in range(3):
                offset = i * 12
                draw.line([(cx, cy + offset*dy), (cx + 60*dx, cy + offset*dy)], fill=GOLD, width=2)
                draw.line([(cx + offset*dx, cy), (cx + offset*dx, cy + 60*dy)], fill=GOLD, width=2)

        # ============================================================
        # WATERMARK (faded logo center)
        # ============================================================
        logo_raw = _load_logo() or _placeholder_logo(200)
        wm = logo_raw.resize((470, 470), Image.LANCZOS)
        wm_a = wm.split()[3].point(lambda p: int(p * 0.07))
        wm.putalpha(wm_a)
        img.paste(wm, ((W - 470) // 2, (H - 470) // 2), wm)
        draw = ImageDraw.Draw(img)

        # ============================================================
        # LOGO (top center)
        # ============================================================
        logo_top = logo_raw.resize((150, 150), Image.LANCZOS)
        img.paste(logo_top, ((W - 150) // 2, 60), logo_top)
        draw = ImageDraw.Draw(img)

        # ============================================================
        # ORGANIZATION NAME
        # ============================================================
        y = 225
        f_org = _font(36, bold=True)
        _center(draw, "KENYA COMMUNITY IN KOREA", y, f_org, NAVY)

        # ============================================================
        # CERTIFICATE TYPE
        # ============================================================
        y += 55
        f_type = _font(28)
        cert_type_text = f"Certificate of {cert.get_cert_type_display()}"
        _center(draw, cert_type_text, y, f_type, BLACK)

        # ============================================================
        # GOLD DIVIDER
        # ============================================================
        y += 45
        div_l, div_r = 250, W - 250
        draw.line([(div_l, y), (W // 2 - 15, y)], fill=GOLD, width=2)
        draw.line([(W // 2 + 15, y), (div_r, y)], fill=GOLD, width=2)
        # Diamond
        cx = W // 2
        draw.polygon([(cx, y-10), (cx+10, y), (cx, y+10), (cx-10, y)], fill=GOLD)

        # ============================================================
        # "This certificate is proudly presented to"
        # ============================================================
        y += 30
        f_presented = _font(20)
        _center(draw, "This certificate is proudly presented to", y, f_presented, GRAY)

        # ============================================================
        # RECIPIENT NAME (large, bold, navy)
        # ============================================================
        y += 40
        f_name = _font(50, bold=True)
        name_w = _center(draw, cert.recipient_name, y, f_name, NAVY)
        # Gold underline
        uy = y + 60
        pad = 80
        name_x = (W - name_w) // 2
        draw.line([(name_x - pad, uy), (name_x + name_w + pad, uy)], fill=GOLD, width=3)

        # ============================================================
        # BODY TEXT
        # ============================================================
        y = uy + 40
        f_body = _font(30)
        clean = re.sub(r'<[^>]+>', '', cert.body or '').replace('&nbsp;', ' ').replace('&amp;', '&').strip()
        lines = _wrap(clean, f_body, W - 500)
        for ln in lines[:6]:
            _center(draw, ln, y, f_body, BODY_COLOR)
            y += 44

        # ============================================================
        # SECOND GOLD DIVIDER
        # ============================================================
        y += 25
        draw.line([(div_l, y), (W // 2 - 15, y)], fill=GOLD, width=2)
        draw.line([(W // 2 + 15, y), (div_r, y)], fill=GOLD, width=2)
        draw.polygon([(cx, y-10), (cx+10, y), (cx, y+10), (cx-10, y)], fill=GOLD)

        # ============================================================
        # DATE AND CERT NUMBER
        # ============================================================
        y += 30
        f_meta = _font(17)
        date_str = cert.issued_at.strftime("%d %B %Y")
        draw.text((120, y), f"Date: {date_str}", fill=GRAY, font=f_meta)
        cn_text = f"No: {cert.cert_number}"
        cn_w, _ = _tw(draw, cn_text, f_meta)
        draw.text((W - 120 - cn_w, y), cn_text, fill=GRAY, font=f_meta)

        # ============================================================
        # SIGNATURE BLOCK (Great Vibes font for name as signature)
        # ============================================================
        issuer = cert.issued_by
        sig_y = H - 320
        sig_cx = W // 3  # Left-of-center

        # Signature: issuer's name in Great Vibes (script/cursive)
        f_sig_script = _font(44, script=True)
        _center_at(draw, issuer.user.full_name, sig_y, sig_cx, f_sig_script, NAVY)

        # Signature line
        sig_y += 55
        line_hw = 130
        draw.line([(sig_cx - line_hw, sig_y), (sig_cx + line_hw, sig_y)], fill=NAVY, width=2)

        # Printed name below line
        sig_y += 12
        f_sig_name = _font(18, bold=True)
        _center_at(draw, issuer.user.full_name, sig_y, sig_cx, f_sig_name, BLACK)

        # Title below name
        sig_y += 28
        f_sig_title = _font(15)
        title = issuer.title or issuer.get_role_display()
        _center_at(draw, title, sig_y, sig_cx, f_sig_title, GRAY)

        # "Kenya Community in Korea" below title
        sig_y += 22
        f_sig_org = _font(13)
        _center_at(draw, "Kenya Community in Korea", sig_y, sig_cx, f_sig_org, GRAY)

        # ============================================================
        # OFFICIAL STAMP (right side — logo + circular text + date)
        # ============================================================
        stamp_cx = W * 2 // 3  # Right-of-center
        stamp_cy = H - 300
        stamp_size = 180

        # Create circular stamp
        stamp_img = Image.new("RGBA", (stamp_size, stamp_size), (0, 0, 0, 0))
        stamp_draw = ImageDraw.Draw(stamp_img)

        # Outer circle
        stamp_draw.ellipse([4, 4, stamp_size-4, stamp_size-4], outline=NAVY, width=3)
        # Inner circle
        stamp_draw.ellipse([14, 14, stamp_size-14, stamp_size-14], outline=NAVY, width=1)

        # Paste logo in center of stamp
        stamp_logo = logo_raw.resize((70, 70), Image.LANCZOS)
        stamp_img.paste(stamp_logo, ((stamp_size-70)//2, 25), stamp_logo)
        stamp_draw = ImageDraw.Draw(stamp_img)

        # Date text at bottom of stamp circle
        f_stamp = _font(13, bold=True)
        date_stamp = cert.issued_at.strftime("%d-%m-%Y")
        sw, _ = _tw(stamp_draw, date_stamp, f_stamp)
        stamp_draw.text(((stamp_size - sw) // 2, stamp_size - 50), date_stamp, fill=NAVY, font=f_stamp)

        # "KCK" text below date
        f_stamp_sm = _font(11, bold=True)
        kw, _ = _tw(stamp_draw, "OFFICIAL", f_stamp_sm)
        stamp_draw.text(((stamp_size - kw) // 2, stamp_size - 35), "OFFICIAL", fill=NAVY, font=f_stamp_sm)

        # Make stamp semi-transparent and paste
        stamp_alpha = stamp_img.split()[3].point(lambda p: int(p * 0.6))
        stamp_img.putalpha(stamp_alpha)
        img.paste(stamp_img, (stamp_cx - stamp_size // 2, stamp_cy - stamp_size // 2), stamp_img)
        draw = ImageDraw.Draw(img)

        # ============================================================
        # BOTTOM BAR: Cert No + QR + Verify Link
        # All content must stay INSIDE borders (borders at 40/60/70 from edge)
        # So nothing below H - 85
        # ============================================================
        base_url = getattr(settings, 'KCK_BASE_URL', 'http://127.0.0.1:8000')
        verify_url = cert.verification_url or f"{base_url}/verify/{cert.cert_number}"
        f_bottom = _font(13)
        f_bottom_bold = _font(13, bold=True)
        f_footer = _font(11)

        # Thin divider line
        div_y = H - 155
        draw.line([(100, div_y), (W - 100, div_y)], fill=GOLD_LIGHT, width=1)

        # Cert number (left)
        row1_y = div_y + 12
        draw.text((100, row1_y), "Certificate No: ", fill=GRAY, font=f_bottom)
        cn_lbl_w, _ = _tw(draw, "Certificate No: ", f_bottom)
        draw.text((100 + cn_lbl_w, row1_y), cert.cert_number, fill=NAVY, font=f_bottom_bold)

        # Verify URL (center of row1)
        verify_text = f"Verify: {verify_url}"
        vw, _ = _tw(draw, verify_text, f_bottom)
        draw.text(((W - vw) // 2, row1_y), verify_text, fill=GRAY, font=f_bottom)

        # QR code (far right)
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color=NAVY, back_color=CREAM).convert("RGB")
            qr_img = qr_img.resize((55, 55), Image.LANCZOS)
            img.paste(qr_img, (W - 140, div_y + 5))
            draw = ImageDraw.Draw(img)
        except Exception as e:
            logger.warning(f"[CERT] QR error: {e}")

        # Website row (below cert number row)
        row2_y = row1_y + 22
        _center(draw, "www.kenyakorea.org  |  kenyakorea@gmail.com  |  010 5084 8654", row2_y, f_footer, GRAY)

        # ============================================================
        # SAVE PNG + PDF
        # ============================================================
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        fn = f"cert_{cert.cert_number.replace('-', '_')}.png"
        cert.image_file.save(fn, ContentFile(buf.getvalue()), save=False)

        rgb = img.convert("RGB")
        buf2 = io.BytesIO()
        rgb.save(buf2, format="PDF", resolution=300)
        fn2 = f"cert_{cert.cert_number.replace('-', '_')}.pdf"
        cert.pdf_file.save(fn2, ContentFile(buf2.getvalue()), save=False)

        cert.status = "published"
        cert.save(update_fields=["image_file", "pdf_file", "status"])
        logger.info(f"[CERT] Generated: {cert.cert_number}")
        return f"Certificate generated: {cert.cert_number}"

    except Exception as e:
        logger.error(f"[CERT] Failed: {e}", exc_info=True)
        cert.status = "failed"
        cert.save(update_fields=["status"])
        return None


@shared_task
def generate_cert_pdf_task(certificate_id):
    return generate_cert_image_task(certificate_id)


@shared_task
def generate_qr_task(certificate_id):
    """Generate standalone QR code for a certificate."""
    from .models import Certificate

    try:
        cert = Certificate.objects.get(id=certificate_id)
        import qrcode
        from PIL import Image

        base_url = getattr(settings, 'KCK_BASE_URL', 'http://127.0.0.1:8000')
        url = cert.verification_url or f"{base_url}/verify/{cert.cert_number}"
        qr = qrcode.QRCode(version=2, box_size=10, border=3)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=(0, 51, 102), back_color="white").convert("RGB")
        qr_img = qr_img.resize((400, 400), Image.LANCZOS)

        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        cert.qr_code.save(f"qr_{cert.cert_number}.png", ContentFile(buf.getvalue()), save=True)
        return f"QR generated for {cert.cert_number}"
    except Exception as e:
        logger.error(f"[QR] Failed: {e}")


@shared_task
def send_cert_email_task(certificate_id):
    """Send certificate to recipient via email."""
    from .models import Certificate
    from django.core.mail import EmailMessage

    try:
        cert = Certificate.objects.select_related("issued_by__user", "recipient_user").get(id=certificate_id)
        recipient_email = None
        if cert.recipient_user and cert.recipient_user.email:
            recipient_email = cert.recipient_user.email

        if not recipient_email:
            logger.info(f"[CERT-EMAIL] No email for {cert.cert_number}")
            return

        msg = EmailMessage(
            subject=f"Your Certificate from Kenya Community in Korea - {cert.get_cert_type_display()}",
            body=f"Dear {cert.recipient_name},\n\nPlease find attached your Certificate of {cert.get_cert_type_display()} from the Kenya Community in Korea.\n\nVerify at: {cert.verification_url}\n\nKind Regards,\n{cert.issued_by.user.full_name}\n{cert.issued_by.title or cert.issued_by.get_role_display()}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )

        if cert.pdf_file and hasattr(cert.pdf_file, 'path') and Path(cert.pdf_file.path).exists():
            msg.attach_file(cert.pdf_file.path)

        msg.send(fail_silently=False)
        logger.info(f"[CERT-EMAIL] Sent to {recipient_email}")
    except Exception as e:
        logger.error(f"[CERT-EMAIL] Failed: {e}")
