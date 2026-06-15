from moviepy.editor import TextClip, CompositeVideoClip

def create_video(text, output_path="output.mp4"):

    clip = TextClip(
        text,
        fontsize=60,
        color='white',
        size=(720, 1280),
        bg_color='black'
    )

    video = CompositeVideoClip([clip.set_duration(5)])

    video.write_videofile(output_path, fps=24)

    return output_path