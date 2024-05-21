'''
Completed. To be reworked into the overall pipeline later.
'''

from PIL import Image
import os


def convert_gif_to_jpeg(gif_path, jpeg_path):
    '''
    This function converts a GIF image to JPEG format.

    Parameters:
        gif_path (string): Path to the input GIF image.
        jpeg_path (string): Path to save the converted JPEG image.

    Returns:
        None
    '''
    try:
        with Image.open(gif_path) as gif:
            # Get the first frame (assuming a single frame GIF)
            # Convert to RGB mode for JPEG compatibility
            frame = gif.convert('RGB')
            frame.save(jpeg_path, format='JPEG')
            print(f"Converted GIF to JPEG: {gif_path} -> {jpeg_path}")

    except OSError as err:
        print(f"Error converting GIF: {err}")


def batch_convert_gifs(gif_folder, output_folder):
    '''
    Temporary first-cut function to batch convert GIFs to JPGs (because the URA website wants to give me an Extra Challenge!). To be modified for pipelining later.

    Parameters:
        gif_folder (string): Path to the folder containing GIF images.
        output_folder (string): Path to the folder to save converted JPEG images.

    Returns:
        None
    '''

    for filename in os.listdir(gif_folder):
        if filename.endswith(".gif"):
            gif_path = os.path.join(gif_folder, filename)

            # Generate unique name for JPEG (avoids overwriting)
            name, _ = os.path.splitext(filename)
            jpeg_path = os.path.join(output_folder, f"{name}.jpg")
            convert_gif_to_jpeg(gif_path, jpeg_path)


def main():
    gif_folder_path = '../data/images/gif'
    jpg_folder_path = '../data/images/jpg'
    batch_convert_gifs(gif_folder_path, jpg_folder_path)


if __name__ == "__main__":
    main()
