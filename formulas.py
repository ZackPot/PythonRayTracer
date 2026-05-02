from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_math_pdf(filename="Ray_Collision_Math.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Ray-Triangle Collision Formulas")

    c.setFont("Helvetica", 12)
    lines = [
        "1. Ray Equation: P = O + tD",
        "   (O = Origin, D = Direction, t = Distance)",
        "",
        "2. Plane Intersection Distance (t):",
        "   t = ((A - O) . N) / (D . N)",
        "   Where A is a vertex and N is the face normal.",
        "",
        "3. Barycentric Coordinates (u, v):",
        "   P - V0 = u(V1 - V0) + v(V2 - V0)",
        "",
        "4. Collision Conditions:",
        "   - t > 0 (Object is in front)",
        "   - u >= 0",
        "   - v >= 0",
        "   - u + v <= 1",
        "",
        "5. Final Collision Coordinates:",
        "   Intersection = O + tD"
    ]

    y = 700
    for line in lines:
        c.drawString(100, y, line)
        y -= 25

    c.save()
    print(f"PDF saved as {filename}")


if __name__ == "__main__":
    generate_math_pdf()
