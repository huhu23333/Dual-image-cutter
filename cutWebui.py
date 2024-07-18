import gradio as gr
from PIL import Image, ImageDraw
import os

png_list1 = []
png_list2 = []
read_index = 0
image_now1 = None
image_now2 = None
cropped_image_now1 = None
cropped_image_now2 = None
inputdir_now = ""
outputdir_now = ""

default_inputdir = "./input/"
default_outputdir = "./output/"

def crop_num(num, low, high):
    if num < low:
        return low
    if num > high:
        return high
    return num

def read_image_now1():
    global image_now1, image_now2
    image_now1 = read_image(inputdir_now, png_list1[read_index])
    image_now2 = read_image(inputdir_now, png_list2[read_index])
    return image_now1, image_now2

def read_image(path, filename):
    if not ((path[-1] == "/") or (path[-1] == "\\")):
        path += "/"
    image_path = path + filename
    image = Image.open(image_path)
    return image

def crop_image_now(x, y, sideLength):
    global cropped_image_now1, cropped_image_now2
    image_draw1, cropped_image1 = crop_image(image_now1, x, y, sideLength)
    image_draw2, cropped_image2 = crop_image(image_now2, x, y, sideLength)
    cropped_image_now1 = cropped_image1
    cropped_image_now2 = cropped_image2
    return image_draw1, cropped_image1, image_draw2, cropped_image2

def crop_image(image, x, y, sideLength):
    image_size = image.size
    cropped_image = image.crop((x, y, x + sideLength, y + sideLength))
    new_image = image.copy()
    image_draw = ImageDraw.Draw(new_image)
    points = [crop_num(x, 0, image_size[0]), crop_num(y, 0, image_size[1]), crop_num(x + sideLength, 0, image_size[0]), crop_num(y + sideLength, 0, image_size[1])]
    color = (255, 0, 0, 128)
    image_draw.line([(points[0], points[1]), (points[2], points[1])], fill=color, width=5)
    image_draw.line([(points[0], points[1]), (points[0], points[3])], fill=color, width=5)
    image_draw.line([(points[2], points[1]), (points[2], points[3])], fill=color, width=5)
    image_draw.line([(points[0], points[3]), (points[2], points[3])], fill=color, width=5)
    return new_image, cropped_image

def read_dir(dir_path, outputdir):
    global png_list1, png_list2, inputdir_now, read_index, outputdir_now
    if not ((outputdir[-1] == "/") or (outputdir[-1] == "\\")):
        outputdir += "/"
    outputdir_now = outputdir
    read_index = 0
    inputdir_now = dir_path
    temp_list = os.listdir(dir_path)
    for i in range(len(temp_list)):
        if temp_list[i][-5:] == "1.png":
            png_list1.append(temp_list[i])
    for i in range(len(png_list1)):
        for j in range(len(temp_list)):
            if (temp_list[j][-5:] == "2.png") and (png_list1[i][:-5] == temp_list[j][:-5]):
                png_list2.append(temp_list[j])
    return f"read {str(temp_list)}", f"{str(read_index+1)}/{len(png_list1)}"

def next_image():
    global read_index
    cropped_image_now1.save(outputdir_now + str(read_index) + "_1.png")
    cropped_image_now2.save(outputdir_now + str(read_index) + "_2.png")
    if read_index < len(png_list1) - 1:
        read_index += 1
        read_image_now1()
    return image_now1, image_now2, f"{str(read_index+1)}/{len(png_list1)}"

app = gr.Blocks()
with app:
    with gr.Row():
        image_original1 = gr.Image(type="pil",interactive=False, scale=1)
        image_original2 = gr.Image(type="pil",interactive=False, scale=1)
        with gr.Column(scale=0):
            image_cropped1 = gr.Image(type="pil",interactive=False)
            image_cropped2 = gr.Image(type="pil",interactive=False)
        
            with gr.Column():
                x_slider = gr.Slider(minimum=-500, maximum=2000, label="X", value=500)
                y_slider = gr.Slider(minimum=-500, maximum=2000, label="Y", value=500)
                sideLength_slider = gr.Slider(minimum=1, maximum=2000, label="Side Length", value=1000)

                crop_button = gr.Button("Crop Image")
                next_button = gr.Button("Next Image")
                text_output1 = gr.Textbox(label="Info", interactive=False)
    
                dir_input = gr.Textbox(label="Input dir", value=default_inputdir)
                dir_output = gr.Textbox(label="Output dir", value=default_outputdir)
                text_output2 = gr.Textbox(label="Input", interactive=False)
                readdir_button = gr.Button("Read dir")
                readimage_button = gr.Button("Read Image")

    readimage_button.click(
        fn=read_image_now1,
        inputs=None,
        outputs=[image_original1, image_original2]
    )

    crop_button.click(
        fn=crop_image_now,
        inputs=[x_slider, y_slider, sideLength_slider],
        outputs=[image_original1, image_cropped1, image_original2, image_cropped2]
    )

    next_button.click(
        fn=next_image,
        inputs=None,
        outputs=[image_original1, image_original2, text_output1]
    )

    readdir_button.click(
        fn=read_dir,
        inputs=[dir_input, dir_output],
        outputs=[text_output2, text_output1]
    )
    

app.launch()
