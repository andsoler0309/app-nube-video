
def get_conversion_command(input_path, output_path, conversion_type):
    conversion_commands = {
        # Convert to MP4 (H.264 video codec and AAC audio codec)
        "mp4": f"ffmpeg -i {input_path} -c:v libx264 -c:a aac {output_path}.mp4",

        # Convert to AVI
        "avi": f"ffmpeg -i {input_path} {output_path}.avi",

        # Convert to MOV
        "mov": f"ffmpeg -i {input_path} {output_path}.mov",

        # Convert to MKV
        "mkv": f"ffmpeg -i {input_path} {output_path}.mkv",

        # Convert to FLV
        "flv": f"ffmpeg -i {input_path} {output_path}.flv",

        # Convert to WMV
        "wmv": f"ffmpeg -i {input_path} -c:v wmv2 -b:v 1024k -c:a wmav2 -b:a 192k {output_path}.wmv",

        # Convert to WEBM (VP9 video codec and Opus audio codec)
        "webm": f"ffmpeg -i {input_path} -c:v libvpx-vp9 -c:a libopus {output_path}.webm",

        # Convert to MPEG (MPEG-1 video codec and MP2 audio codec)
        "mpeg": f"ffmpeg -i {input_path} -c:v mpeg1video -c:a mp2 {output_path}.mpeg",
    }

    return conversion_commands.get(conversion_type, None)
