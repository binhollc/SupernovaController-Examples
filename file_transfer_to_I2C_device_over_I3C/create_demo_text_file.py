# Define the phrase to be repeated
phrase = "Binho Supernova Demo"

# Calculate the size of the phrase in bytes
phrase_size = len(phrase.encode('utf-8'))

# Calculate how many times the phrase needs to be repeated to reach 30 KB
target_size = 30 * 1024  # 30 KB in bytes
repeats = target_size // phrase_size

# Create the content by repeating the phrase
content = phrase * repeats

# If the content is slightly under 30 KB, pad with additional characters
if len(content.encode('utf-8')) < target_size:
    content += phrase[:target_size - len(content.encode('utf-8'))]

# Write the content to a .txt file
with open("Binho_Supernova_Demo.txt", "w") as file:
    file.write(content)

print("File created successfully.")