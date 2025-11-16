import markdown
import pdfkit
import os

# Paths
md_path = os.path.join(os.path.dirname(__file__), 'USER_MANUAL.md')
pdf_path = os.path.join(os.path.dirname(__file__), 'USER_MANUAL.pdf')

# Read markdown
with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert markdown to HTML
html = markdown.markdown(md_text, extensions=['extra', 'toc'])

# Add basic styling for PDF readability
html = f"""
<html>
<head>
    <meta charset='utf-8'>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2em; line-height: 1.6; }}
        h1 {{ color: #1DA1F2; border-bottom: 3px solid #1DA1F2; padding-bottom: 10px; }}
        h2 {{ color: #14171A; border-bottom: 1px solid #AAB8C2; padding-bottom: 5px; margin-top: 30px; }}
        h3 {{ color: #657786; margin-top: 25px; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; font-family: monospace; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; border-left: 4px solid #1DA1F2; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f8f8f8; }}
        ul, ol {{ margin-left: 2em; }}
        li {{ margin-bottom: 5px; }}
        strong {{ color: #14171A; }}
    </style>
</head>
<body>
{html}
</body>
</html>
"""

# Common wkhtmltopdf installation paths on Windows
possible_paths = [
    r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',  # User's actual path
    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
    r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
    r'C:\wkhtmltopdf\bin\wkhtmltopdf.exe',
    'wkhtmltopdf'  # If it's in PATH
]

config = None
for path in possible_paths:
    try:
        if path == 'wkhtmltopdf':
            # Try using default PATH
            config = None
            break
        elif os.path.exists(path):
            config = pdfkit.configuration(wkhtmltopdf=path)
            print(f"✓ Found wkhtmltopdf at: {path}")
            break
    except:
        continue

# PDF options
options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'enable-local-file-access': None
}

try:
    # Convert HTML to PDF
    if config:
        pdfkit.from_string(html, pdf_path, options=options, configuration=config)
    else:
        pdfkit.from_string(html, pdf_path, options=options)
    print(f"✅ PDF generated successfully at: {pdf_path}")
except Exception as e:
    print(f"❌ Error generating PDF: {e}")
    print("💡 Tried these wkhtmltopdf paths:")
    for path in possible_paths:
        exists = "✅" if (path == 'wkhtmltopdf' or os.path.exists(path)) else "❌"
        print(f"   {exists} {path}")
    print("\n🔧 If none of these paths work, please check where wkhtmltopdf is installed.")
