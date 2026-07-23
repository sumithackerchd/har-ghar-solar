import re

with open("app.py", "r") as f:
    content = f.read()

# Routes to add
routes_addition = """
@app.route("/solar-tools")
def solar_tools():
    return render_template("solar_tools.html")

@app.route("/downloads")
def downloads():
    return render_template("downloads.html")

"""

error_handlers_marker = "# ==========================\n# ERROR HANDLERS\n# =========================="
if error_handlers_marker in content:
    content = content.replace(error_handlers_marker, routes_addition + error_handlers_marker)
else:
    print("Could not find error handlers marker")

with open("app.py", "w") as f:
    f.write(content)

print("app.py patched with solar tools routes.")
