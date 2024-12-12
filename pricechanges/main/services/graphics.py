import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.utils.safestring import mark_safe

# Generate plot
plt.plot([1, 2, 3, 4], [4, 3, 2, 1], 'go--', linewidth=2, markersize=12)
plt.ylabel('some numbers')

# Convert plot to base64-encoded image
buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
img_str = base64.b64encode(buffer.read()).decode('utf-8')

# Generate HTML with embedded image
graph = mark_safe(f'<img src="data:image/png;base64,{img_str}" height="30%" width="30%">')


