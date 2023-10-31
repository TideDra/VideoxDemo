import gradio as gr
import os
import datetime
import time
from threading import Thread
from loguru import logger
def makeVTT(captions, output_dir,video_name):
    with open(os.path.join(output_dir,f"{video_name}.vtt"), "w") as f:
        f.write("WEBVTT\n")
        for caption in captions:
            start_time = caption[0][0]
            end_time = caption[0][1]
            cap = caption[1]
            start_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(seconds=start_time)
            end_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(seconds=end_time)
            f.write(f"{start_time.strftime('%H:%M:%S')}.000 --> {end_time.strftime('%H:%M:%S')}.000\n")
            f.write(f"{cap}\n\n")

def clear_tmp(tmp_dir='demo_tmp',cycle=3600):
    start_time = time.time()
    while True:
        time.sleep(cycle/2)
        files = os.listdir(tmp_dir)
        for file in files:
            file_path = os.path.join(tmp_dir,file)
            stay_time = os.path.getctime(file_path)-start_time
            if stay_time > cycle:
                os.remove(file_path)
        logger.info("Temp files cleared.")
def launch_demo(chatbot,example_dir):
    '''
    chatbot(video) -> captions
    video: path to video
    captions should be this format: [[(start_time, end_time),caption],[(start_time, end_time),caption],...]]
        e.g. [[(0,3),'hello world'],[(3,6),'hello world'],[(6,9),'hello world']]
    '''
    os.system("mkdir -p demo_tmp")
    os.system("rm -rf demo_tmp/*")
    def VideoUnderstanding(video_inp):
        captions=chatbot(video_inp)
        video_name = time.time()
        makeVTT(captions, "demo_tmp/",video_name)
        
        os.system(f"ffmpeg -hide_banner -loglevel error -y -i {video_inp} -i demo_tmp/{video_name}.vtt -map 0:0 -map 0:1 -map 1 -c:a copy -c:v copy -c:s copy demo_tmp/{video_name}.mkv")
        video_html = f" <style>::cue {{color: white;background-color: transparent;font-family: Arial, sans-serif;font-size: 28px;text-align: center;padding: 5px;border-radius: 5px;text-shadow: -1.5px -1.5px 0 black, 1.5px -1.5px 0 black, -1.5px 1.5px 0 black, 1.5px 1.5px 0 black;}}</style><video width='800' height='600' controls download='file=output_video.mkv'>><source src='file=demo_tmp/{video_name}.mkv' type='video/mp4'><track kind='subtitles' src='file=demo_tmp/{video_name}.vtt' srclang='en' label='English'  default></video>"
        return video_html
    logo_path = "/data/code/X-CLIP/logo_with_text.png"
    logo_url = "https://raw.githubusercontent.com/TideDra/X-CLIP/finegrained_caption/logo_with_text.png"
    examples = os.listdir(example_dir)
    examples_paths = [os.path.join(example_dir,example) for example in examples]
    with gr.Blocks(title="VideoX") as demo:
        gr.Markdown(f"<p align='center'><img src='{logo_url}' width='400'> <br></p>")
        with gr.Row():
            with gr.Column():
                video_inp = gr.Video(label='Input Video')
                btn = gr.Button(value="Submit")
            with gr.Column():
                video_out = gr.HTML(label='Output Video')
                #clearbtn = gr.ClearButton(value="Clear",components=[video_inp,video_out])
            btn.click(VideoUnderstanding,inputs=[video_inp],outputs=[video_out])
        gr.Examples(examples_paths,
                    [video_inp],
                    video_out,
                    VideoUnderstanding)
    clear_tmp_thread = Thread(target=clear_tmp)
    clear_tmp_thread.start()
    demo.launch(share=True)
