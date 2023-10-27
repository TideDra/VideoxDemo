import gradio as gr
import os
import datetime
def makeVTT(captions, output_dir):
    with open(os.path.join(output_dir,"subtitles.vtt"), "w") as f:
        f.write("WEBVTT\n")
        for caption in captions:
            start_time = caption[0][0]
            end_time = caption[0][1]
            cap = caption[1]
            start_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(seconds=start_time)
            end_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(seconds=end_time)
            f.write(f"{start_time.strftime('%H:%M:%S')}.000 --> {end_time.strftime('%H:%M:%S')}.000\n")
            f.write(f"{cap}\n\n")


def launch_demo(chatbot):
    '''
    chatbot(video) -> captions
    video: path to video
    captions should be this format: [[(start_time, end_time),caption],[(start_time, end_time),caption],...]]
        e.g. [[(0,3),'hello world'],[(3,6),'hello world'],[(6,9),'hello world']]
    '''
    os.system("mkdir -p demo_tmp")
    def VideoUnderstanding(video_inp):
        captions=chatbot(video_inp)

        print(captions)
        makeVTT(captions, "demo_tmp/")
        video_html = f"<video width='800' height='600' controls><source src='file={video_inp}' type='video/mp4'><track kind='subtitles' src='file=demo_tmp/subtitles.vtt' srclang='en' label='English'  default></video>"
        return video_html
    logo_path = "/data/code/X-CLIP/logo_with_text.png"
    logo_url = "https://raw.githubusercontent.com/TideDra/X-CLIP/finegrained_caption/logo_with_text.png"

    with gr.Blocks(title="VideoX") as demo:
        gr.Markdown(f"<p align='center'><img src='{logo_url}' width='400'> <br></p>")
        with gr.Row():
            with gr.Column():
                video_inp = gr.Video(label='Input Video')
                btn = gr.Button(value="Submit")
            video_out = gr.HTML(label='Output Video')
            btn.click(VideoUnderstanding,inputs=[video_inp],outputs=[video_out])
        gr.Examples([["examples/nvzkbpt9z7k.mp4"]
                    ,["examples/hx_zCVNh4aM.mp4"]
                    ,["examples/QNc82qD2AtM.mp4"]
                    ,["examples/efmCEJgfl2o.mp4"]],
                    [video_inp],
                    video_out,
                    VideoUnderstanding)

    demo.launch(share=True)