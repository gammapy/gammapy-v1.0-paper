from pathlib import Path

TEMPLATE = "\\input{{{0}}}"
PATH_TEXT = Path("src/text")


def merge_text_files(text, filenames):
    """Merge tex files"""
    for filename in filenames:
        path = filename.parent.relative_to(PATH_TEXT.parent)
        file = str(path) + "/" + filename.stem
        template = TEMPLATE.format(file)

        with open(filename, "r") as f_sub:
            file_content = f_sub.read()
            text = text.replace(template, file_content)

    return text


if __name__ == "__main__":
    with (PATH_TEXT / "../ms.tex").open("r") as f:
        text = f.read()

    filenames = PATH_TEXT.glob("*.tex")
    text = merge_text_files(text=text, filenames=filenames)

    filenames = (PATH_TEXT / "2-package-subsections").glob("*.tex")
    text = merge_text_files(text=text, filenames=filenames)

    filenames = (PATH_TEXT / "3-applications-subsections").glob("*.tex")
    text = merge_text_files(text=text, filenames=filenames)

    path = PATH_TEXT / ".."
    path.mkdir(exist_ok=True)

    with (path / "ms-review.tex").open("w") as f:
        f.write(text)
