import requests
import os

folder = r'C:\Users\bhanu\OneDrive\Desktop\Combat\backend\datasets\sample_documents'

for fname in sorted(os.listdir(folder)):
    if fname.endswith('.txt'):
        fpath = os.path.join(folder, fname)
        title = fname.replace('.txt', '').replace('_', ' ').title()
        with open(fpath, 'rb') as f:
            r = requests.post(
                'http://localhost:8000/api/documents/upload',
                files={'file': (fname, f, 'text/plain')},
                data={'title': title}
            )
        if r.status_code == 200:
            doc = r.json()
            print(f"✅ Uploaded: {fname}  (ID: {doc.get('id')})")
        else:
            print(f"❌ Failed:   {fname}  -> {r.status_code} {r.text}")

print("\nDone! Refresh the Analyze page in your browser.")
