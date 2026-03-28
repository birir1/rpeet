"""
Generic image upload endpoint used by the rich text editor (CKEditor) in the frontend.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
import os
import uuid

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageUploadView(APIView):
    """
    POST /kck/media/upload/ -- handles image uploads from the CKEditor rich text editor.

    Security measures:
    - We validate BOTH the file extension AND the Content-Type header. Checking only
      the extension is insufficient because an attacker could rename a malicious file
      to .jpg. Checking only Content-Type is also insufficient because it can be spoofed.
      Together, they raise the bar significantly against upload-based attacks.
    - We replace the original filename with a UUID to prevent path traversal attacks
      (e.g., filenames like "../../etc/passwd.jpg") and to avoid filename collisions
      when multiple users upload files with the same name.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('upload')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(file.name)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if ext not in allowed_extensions:
            return Response({'error': f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File too large. Maximum size is 5MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save with a UUID-based filename to prevent path traversal and collisions
        ext = os.path.splitext(file.name)[1].lower()
        filename = f"uploads/{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # Return URL in CKEditor format
        url = f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL}{filename}"
        return Response({'url': url})
