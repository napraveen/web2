import os

def get_image_names(directory):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')  # Add more extensions if needed
    image_names = []

    for filename in os.listdir(directory):
        if filename.lower().endswith(image_extensions):
            image_names.append(filename)

    return image_names

# Replace 'path_to_directory' with the path to your directory containing images
directory = './crackedimages'
image_names = get_image_names(directory)

for name in image_names:
    print(name)
