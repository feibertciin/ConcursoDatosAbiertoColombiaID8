import urllib.request
import re

url = "https://snies.mineducacion.gov.co/portal/ESTADISTICAS/Bases-consolidadas/"
print("Conectando a:", url)

try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
    print("Buscando URLs...")
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    
    # Filtrar enlaces relevantes (que contengan .zip, .xlsx, .xls, .csv, o datos)
    relevant_links = []
    for link in links:
        if any(ext in link.lower() for ext in ['.zip', '.xlsx', '.xls', '.csv', 'descargar', 'resource', 'bases']):
            relevant_links.append(link)
            
    print(f"Total enlaces encontrados: {len(links)}")
    print(f"Enlaces relevantes: {len(relevant_links)}")
    for r_link in set(relevant_links):
        print(" -", r_link)

except Exception as e:
    print("Error:", e)
