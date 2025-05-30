import base64

file_path = "Cute_Nurse_Pictures-removebg-preview.png"

with open(file_path, "rb") as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    data_uri = f"data:image/png;base64,{b64_string}"
    print(data_uri)