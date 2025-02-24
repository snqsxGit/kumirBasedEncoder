from flask import Flask, request, render_template, url_for
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_and_convert_to_bw(image_path, new_width=50, new_height=50):
    img = Image.open(image_path).convert('L')
    img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
    bw_img = img.point(lambda x: 0 if x < 128 else 255, '1')
    return bw_img

def image_to_grid(bw_img):
    pixels = bw_img.load()
    width, height = bw_img.size
    return [[1 if pixels[x, y] == 0 else 0 for x in range(width)] for y in range(height)]

def generate_kumir_robot_code(grid):
    n, m = len(grid), len(grid[0])
    commands = ["использовать Робот", "алг", "нач"]
    current_x, current_y = 1, 1
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                while current_y < i + 1:
                    commands.append("вниз")
                    current_y += 1
                while current_y > i + 1:
                    commands.append("вверх")
                    current_y -= 1
                while current_x < j + 1:
                    commands.append("вправо")
                    current_x += 1
                while current_x > j + 1:
                    commands.append("влево")
                    current_x -= 1
                commands.append("закрасить")
    commands.append("кон")
    return "\n".join(commands)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Файл не найден!"
        file = request.files['file']
        if file.filename == '':
            return "Файл не выбран!"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            bw_img = load_and_convert_to_bw(file_path, new_width=50, new_height=50)
            grid = image_to_grid(bw_img)
            code = generate_kumir_robot_code(grid)
            
            output_filename = os.path.splitext(filename)[0] + "_kumir.txt"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            return render_template("result.html", code=code)
    return render_template("index.html")

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
