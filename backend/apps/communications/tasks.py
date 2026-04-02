"""
Async tasks for generating communication PDFs, images, and sending bulk emails.
Author: Meshack Tirop

I built this module to handle the heavy lifting of document generation off the
main request thread. When a leader publishes a communication, the view kicks off
a Celery task here so the user gets an instant response while Pillow renders a
full A4 letterhead image in the background.

Design decisions:
- I use Pillow (PIL) exclusively for image generation rather than WeasyPrint or
  wkhtmltopdf because it gives me pixel-perfect control over the letterhead
  layout without requiring system-level HTML rendering dependencies. The PDF is
  then produced directly from the rendered PIL image at 300 DPI, which guarantees
  the PDF looks identical to the PNG -- no CSS-to-print surprises.
- Bulk emails are sent one-at-a-time rather than using BCC so that failures are
  isolated per recipient and we get accurate sent/failed counts.
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

logger = logging.getLogger("apps.communications")

# ---------------------------------------------------------------------------
# Brand constants
# ---------------------------------------------------------------------------
DEEP_BLUE = (0, 51, 102)
RED = (187, 0, 0)
BLACK = (17, 17, 17)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
MUTED = (140, 140, 140)
LIGHT_GRAY = (200, 200, 200)
BODY_COLOR = (40, 40, 40)
GOLD = (180, 150, 50)

# A4 portrait at 300 DPI
PAGE_W = 2480
PAGE_H = 3508

# Margins
LEFT = 200
RIGHT = 200
CONTENT_W = PAGE_W - LEFT - RIGHT

# Logo search paths
LOGO_PATHS = [
    Path(settings.BASE_DIR) / "static" / "images" / "kck-logo.png",
    Path(settings.BASE_DIR).parent / "frontend" / "public" / "images" / "kck-logo.png",
]


def _get_font_path(font_name="DejaVuSans.ttf"):
    """Find a font file cross-platform.

    I implemented a multi-tier font resolution strategy because this code runs
    on three very different environments: my Windows dev machine, a Linux Docker
    container in production, and occasionally macOS for other contributors.
    The lookup order is: bundled project fonts first (most reliable), then
    platform-specific system font directories. If nothing is found, Pillow's
    built-in bitmap font is used as a last resort -- it's ugly but won't crash.
    """
    # Check bundled fonts first (relative to project)
    bundled = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'fonts', font_name)
    if os.path.exists(bundled):
        return bundled

    # Platform-specific font directories
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


def _font(size, bold=False):
    from PIL import ImageFont

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
    draw.text(((PAGE_W - w) // 2, y), text, fill=fill, font=font)


def _right(draw, text, y, font, fill, rx=None):
    rx = rx or PAGE_W - RIGHT
    w, _ = _tw(draw, text, font)
    draw.text((rx - w, y), text, fill=fill, font=font)


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
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def _load_logo():
    from PIL import Image
    for p in LOGO_PATHS:
        if p.exists():
            try: return Image.open(p).convert("RGBA")
            except: pass
    return None


def _placeholder_logo(size=200):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([5, 5, size-5, size-5], outline=DEEP_BLUE, width=6)
    f = _font(size // 3, bold=True)
    w, h = _tw(d, "KCK", f)
    d.text(((size-w)//2, (size-h)//2), "KCK", fill=DEEP_BLUE, font=f)
    return img


def _ordinal(dt):
    d = dt.day
    s = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{d}{s} {dt.strftime('%B, %Y')}."


def _strip_html(html):
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.I)
    text = re.sub(r'</p>', '\n\n', text, flags=re.I)
    text = re.sub(r'</li>', '\n', text, flags=re.I)
    text = re.sub(r'<li[^>]*>', '    • ', text, flags=re.I)
    text = re.sub(r'</div>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    paras = re.split(r'\n\s*\n', text)
    return [' '.join(p.split()) for p in paras if p.strip()]


# ---------------------------------------------------------------------------
@shared_task
def generate_comm_image_task(communication_id):
    """Generate professional KCK letterhead PNG + PDF.

    I designed the letterhead layout to mirror the official KCK physical
    letterhead: logo on the left, organisation name centered in red, contact
    details stacked on the right. The tri-color bar (black/red/blue) represents
    the Kenyan flag colors and provides visual brand consistency.

    The rendering pipeline is: build a full A4-at-300DPI PIL Image -> save as
    PNG -> convert the same image to PDF at 300 DPI. This approach means I only
    render once and both outputs are pixel-identical, avoiding the drift you'd
    get from separate HTML-to-PDF and HTML-to-image pipelines.
    """
    from .models import Communication

    logger.info(f"[COMM] Generating for {communication_id}")

    try:
        comm = Communication.objects.select_related("sender__user").get(id=communication_id)
    except Communication.DoesNotExist:
        logger.error(f"[COMM] Not found: {communication_id}")
        return

    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (PAGE_W, PAGE_H), WHITE)
        draw = ImageDraw.Draw(img)

        # --- Watermark (faded center logo) ---
        logo_raw = _load_logo() or _placeholder_logo(200)
        wm = logo_raw.resize((700, 700), Image.LANCZOS)
        wm_a = wm.split()[3].point(lambda p: int(p * 0.06))
        wm.putalpha(wm_a)
        img.paste(wm, ((PAGE_W - 700) // 2, (PAGE_H - 700) // 2), wm)
        draw = ImageDraw.Draw(img)

        # ============================================================
        # HEADER BLOCK (y: 60 - 260)
        # ============================================================
        # Logo (left) — 180x180
        logo_h = logo_raw.resize((180, 180), Image.LANCZOS)
        img.paste(logo_h, (LEFT, 60), logo_h)
        draw = ImageDraw.Draw(img)

        # Organisation name (center, large, bold, red)
        f_org = _font(52, bold=True)
        _center(draw, "KENYA COMMUNITY", 80, f_org, RED)
        _center(draw, "IN KOREA.", 140, f_org, RED)

        # Contact info (right side, stacked)
        f_contact = _font(26)
        f_contact_icon = _font(26, bold=True)
        rx = PAGE_W - RIGHT
        cy = 75
        # Email
        _right(draw, "info@kenyakorea.com", cy, f_contact, GRAY, rx)
        cy += 38
        # Website
        _right(draw, "www.kenyakorea.com", cy, f_contact, GRAY, rx)
        cy += 38
        # Phone
        _right(draw, "010 5084 8654", cy, f_contact, GRAY, rx)

        # ============================================================
        # TRI-COLOR BAR (Kenya flag: Black | Red | Blue)
        # ============================================================
        bar_y = 280
        bar_h = 10
        seg = PAGE_W // 3
        draw.rectangle([0, bar_y, seg, bar_y + bar_h], fill=BLACK)
        draw.rectangle([seg, bar_y, 2*seg, bar_y + bar_h], fill=RED)
        draw.rectangle([2*seg, bar_y, PAGE_W, bar_y + bar_h], fill=DEEP_BLUE)

        # ============================================================
        # DATE (right-aligned, ordinal format)
        # ============================================================
        y = bar_y + 60
        f_date = _font(32, bold=True)
        f_ref = _font(28, bold=True)
        f_ref_val = _font(28)
        f_to_label = _font(30, bold=True)
        f_to_val = _font(30)

        date_str = _ordinal(comm.created_at)
        _right(draw, date_str, y, f_date, BLACK)

        # ============================================================
        # REFERENCE NUMBER (left-aligned: Ref: KCK/2026/001)
        # ============================================================
        y += 50
        draw.text((LEFT, y), "Ref: ", fill=GRAY, font=f_ref)
        ref_w, _ = _tw(draw, "Ref: ", f_ref)
        draw.text((LEFT + ref_w, y), comm.reference_number, fill=DEEP_BLUE, font=f_ref)

        # ============================================================
        # TO: line (left-aligned: To: All Registered / Members Only / etc.)
        # ============================================================
        y += 45
        audience_labels = {
            "all": "All Registered Kenyans in Korea",
            "members_only": "KCK Members Only",
            "city": f"Kenyans in {(comm.audience_filter or 'Korea').title()}",
            "category_group": f"All {(comm.audience_filter or '').title()}s",
        }
        to_text = audience_labels.get(comm.audience, "All Registered Kenyans in Korea")
        draw.text((LEFT, y), "To: ", fill=GRAY, font=f_to_label)
        to_w, _ = _tw(draw, "To: ", f_to_label)
        draw.text((LEFT + to_w, y), to_text, fill=BLACK, font=f_to_val)

        # ============================================================
        # SUBJECT (centered, underlined, blue)
        # ============================================================
        y += 70
        f_subj = _font(38, bold=True)
        subj_text = comm.subject
        sw, sh = _tw(draw, subj_text, f_subj)
        sx = (PAGE_W - sw) // 2
        draw.text((sx, y), subj_text, fill=DEEP_BLUE, font=f_subj)
        # Underline
        uy = y + sh + 8
        draw.line([(sx, uy), (sx + sw, uy)], fill=DEEP_BLUE, width=3)

        # ============================================================
        # BODY TEXT (left-aligned, proper size, paragraph spacing)
        # ============================================================
        y = uy + 60
        f_body = _font(32)
        f_body_bold = _font(32, bold=True)
        line_h = 48
        para_gap = 30
        max_body_y = PAGE_H - 700  # Reserve for signature + footer

        paragraphs = _strip_html(comm.body)

        # Greeting line
        draw.text((LEFT, y), "Dear Fellow Kenyans in Korea (KCK Family),", fill=BODY_COLOR, font=f_body)
        y += line_h + para_gap

        for para in paragraphs:
            if y >= max_body_y:
                break
            lines = _wrap(para, f_body, CONTENT_W)
            for ln in lines:
                if y >= max_body_y:
                    break
                draw.text((LEFT, y), ln, fill=BODY_COLOR, font=f_body)
                y += line_h
            y += para_gap

        # ============================================================
        # CLOSING + SIGNATURE
        # ============================================================
        sig_y = max(y + 60, PAGE_H - 650)
        f_closing = _font(32)
        f_name = _font(34, bold=True)
        f_title = _font(28)

        draw.text((LEFT, sig_y), "Kind Regards,", fill=BLACK, font=f_closing)
        sig_y += 60

        sender = comm.sender

        # Signature image (if available)
        if sender.signature and hasattr(sender.signature, 'path'):
            try:
                sp = Path(sender.signature.path)
                if sp.exists():
                    si = Image.open(str(sp)).convert("RGBA")
                    si = si.resize((320, 160), Image.LANCZOS)
                    img.paste(si, (LEFT, sig_y), si)
                    draw = ImageDraw.Draw(img)
                    sig_y += 170
            except Exception as e:
                logger.warning(f"[COMM] Sig error: {e}")

        # Name
        draw.text((LEFT, sig_y), sender.user.full_name, fill=BLACK, font=f_name)
        sig_y += 50

        # Title
        title = sender.title or sender.get_role_display()
        draw.text((LEFT, sig_y), title, fill=GRAY, font=f_title)

        # Stamp overlay (if available)
        if sender.stamp and hasattr(sender.stamp, 'path'):
            try:
                stp = Path(sender.stamp.path)
                if stp.exists():
                    st = Image.open(str(stp)).convert("RGBA")
                    st = st.resize((280, 280), Image.LANCZOS)
                    st_a = st.split()[3].point(lambda p: int(p * 0.45))
                    st.putalpha(st_a)
                    img.paste(st, (LEFT + 400, sig_y - 200), st)
                    draw = ImageDraw.Draw(img)
            except Exception as e:
                logger.warning(f"[COMM] Stamp error: {e}")

        # ============================================================
        # FOOTER
        # ============================================================
        f_footer = _font(22)

        # Thin divider line
        fy = PAGE_H - 120
        draw.line([(LEFT, fy), (PAGE_W - RIGHT, fy)], fill=LIGHT_GRAY, width=2)

        # Footer text
        fy += 15
        _center(draw, "Kenya Community in Korea  |  www.kenyakorea.com  |  info@kenyakorea.com",
                fy, f_footer, MUTED)

        # Bottom tri-color bar
        by = PAGE_H - 50
        bh = 8
        draw.rectangle([0, by, seg, by + bh], fill=BLACK)
        draw.rectangle([seg, by, 2*seg, by + bh], fill=RED)
        draw.rectangle([2*seg, by, PAGE_W, by + bh], fill=DEEP_BLUE)

        # ============================================================
        # SAVE PNG
        # ============================================================
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        fn = f"comm_{comm.reference_number.replace('/', '_')}.png"
        comm.image_file.save(fn, ContentFile(buf.getvalue()), save=False)

        # ============================================================
        # SAVE PDF (from PNG at 300 DPI)
        # ============================================================
        rgb = img.convert("RGB")
        buf2 = io.BytesIO()
        rgb.save(buf2, format="PDF", resolution=300)
        fn2 = f"comm_{comm.reference_number.replace('/', '_')}.pdf"
        comm.pdf_file.save(fn2, ContentFile(buf2.getvalue()), save=False)

        # ============================================================
        # UPDATE STATUS
        # ============================================================
        comm.status = "published"
        comm.published_at = timezone.now()
        comm.save(update_fields=["image_file", "pdf_file", "status", "published_at"])
        logger.info(f"[COMM] Published: {comm.reference_number}")
        return f"Generated {comm.reference_number}"

    except Exception as e:
        logger.error(f"[COMM] Failed: {e}", exc_info=True)
        try:
            comm.status = "failed"
            comm.save(update_fields=["status"])
        except:
            pass


# ---------------------------------------------------------------------------
@shared_task
def generate_comm_pdf_task(communication_id):
    """Backward compat — delegates to image task."""
    return generate_comm_image_task(communication_id)


# ---------------------------------------------------------------------------
@shared_task
def send_bulk_email_task(subject, body, recipient_emails, from_email=None):
    """Send bulk HTML email.

    I chose to send emails individually (one per recipient) rather than using
    BCC for two reasons: (1) per-recipient error tracking -- if one address
    bounces, the rest still go out and we know exactly which failed, and
    (2) some SMTP providers rate-limit or reject large BCC lists. The tradeoff
    is slightly more SMTP overhead, but for our community size (~500 members)
    this is well within acceptable limits.
    """
    from django.core.mail import EmailMessage

    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    sent, failed = 0, 0
    for addr in recipient_emails:
        try:
            msg = EmailMessage(subject=subject, body=body, from_email=from_email, to=[addr])
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            sent += 1
        except Exception as e:
            logger.error(f"[EMAIL] Failed {addr}: {e}")
            failed += 1

    logger.info(f"[EMAIL] Sent: {sent}, Failed: {failed}")
    return {"sent": sent, "failed": failed}
