# -*- coding: utf-8 -*-
"""Generate + verify the QR code for the live app URL.

Outputs:
  qr_zpd.png  — print-quality PNG (also copied to the Drive meeting folder later)
  qr_zpd.svg  — compact SVG path, embedded into slides.html
Verification: decode the PNG with zxing-cpp and assert it equals the URL.
"""
import qrcode
import qrcode.image.svg

URL = "https://tomhagiladi.github.io/zpd-learning-journey/"
OUT = r"C:\Users\tomha\AppData\Local\Temp\claude\ono4"

# --- PNG (print quality) ---
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=14, border=4)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="#1E2B33", back_color="white")
img.save(OUT + r"\qr_zpd.png")
print("PNG size:", img.size)

# --- SVG (for slides embedding) ---
qr2 = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
qr2.add_data(URL)
qr2.make(fit=True)
svg_img = qr2.make_image(image_factory=qrcode.image.svg.SvgPathImage)
svg_bytes = svg_img.to_string()
with open(OUT + r"\qr_zpd.svg", "wb") as f:
    f.write(svg_bytes)
print("SVG bytes:", len(svg_bytes))

# --- Verify by decoding the PNG ---
import zxingcpp
from PIL import Image
decoded = zxingcpp.read_barcode(Image.open(OUT + r"\qr_zpd.png"))
print("decoded:", decoded.text if decoded else None)
assert decoded and decoded.text == URL, "QR VERIFICATION FAILED!"
print("QR VERIFIED OK ->", URL)
