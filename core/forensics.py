import email
from email import policy
from email.parser import BytesParser
import re
from fpdf import FPDF
import pandas as pd
import random

class ForensicToolkit:
    """
    Handles static analysis: Parsing EML, Extracting IPs, and PDF Generation.
    """

    @staticmethod
    def parse_eml(file_buffer):
        """Parses .eml bytes into structured headers and body."""
        try:
            msg = BytesParser(policy=policy.default).parsebytes(file_buffer.getvalue())
            
            # Extract Body
            body = msg.get_body(preferencelist=('plain', 'html'))
            content = body.get_content() if body else "No readable body found."
            
            # Extract Headers (Standardized)
            headers = {
                "Subject": msg.get('subject', 'Unknown'),
                "From": msg.get('from', 'Unknown'),
                "To": msg.get('to', 'Unknown'),
                "Date": msg.get('date', 'Unknown'),
                "Return-Path": msg.get('return-path', 'None'),
                "X-Mailer": msg.get('x-mailer', 'None'),
                "Received": str(msg.get_all('received', [])) # Critical for IP tracing
            }
            return headers, content
        except Exception as e:
            return {"Error": str(e)}, ""

    @staticmethod
    def extract_ips(text_blob):
        """Regex to find public IPv4 addresses."""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        all_ips = re.findall(ip_pattern, str(text_blob))
        
        # Filter out Local/Private IPs (127.0.0.1, 10.x, 192.168.x)
        public_ips = [
            ip for ip in set(all_ips) 
            if not ip.startswith(('127.', '10.', '192.168.', '172.16.'))
        ]
        return list(public_ips)

    @staticmethod
    def get_geo_dataframe(ips):
        """
        Generates simulated Geo-Location data for the Map Feature.
        """
        data = []
        for i, ip in enumerate(ips[:15]): # Limit to 15 hops
            # Use hash to make "random" location consistent for the same IP
            random.seed(ip)
            
            # Distribute roughly around major server hubs (US, EU, Asia)
            regions = [
                (37.09, -95.71), # US
                (51.16, 10.45),  # Germany
                (35.67, 139.65), # Japan
                (55.75, 37.61),  # Russia
                (-25.27, 133.77) # Australia
            ]
            base_lat, base_lon = random.choice(regions)
            
            # Add jitter
            lat = base_lat + random.uniform(-10, 10)
            lon = base_lon + random.uniform(-10, 10)
            
            data.append({
                "lat": lat,
                "lon": lon,
                "IP Address": ip,
                "Location Context": "Suspicious Node" if i == 0 else "Routing Server",
                "size": 20 if i == 0 else 5 # Make the first IP bigger
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_pdf(title, headers, content_a, content_b=None):
        """Generates a PDF Report."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"PhishGuard Report: {title}", ln=True, align='C')
        pdf.ln(10)
        
        # Metadata
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "1. Artifact Metadata", ln=True)
        pdf.set_font("Arial", '', 10)
        
        if headers:
            for k, v in list(headers.items())[:5]: # First 5 headers
                safe_v = str(v).encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 6, f"{k}: {safe_v[:80]}...", ln=True)
        else:
            pdf.cell(0, 6, "Type: Image Screenshot", ln=True)
            
        pdf.ln(10)
        
        # Analysis A
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. AI Forensic Analysis", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, content_a.encode('latin-1', 'replace').decode('latin-1'))
        
        # Analysis B (For Comparison)
        if content_b:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "3. Secondary Model Analysis", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, content_b.encode('latin-1', 'replace').decode('latin-1'))
            
        return pdf.output(dest='S').encode('latin-1')