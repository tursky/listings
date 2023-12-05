import os
import platform
import subprocess
import sys
import json
import datetime


def read(filename):
    with open(filename, "r", encoding="utf=8") as file:
        return json.load(file)


config = read("configurations.json")


ROOT = config.get("src")
PREPRINT = config.get("pdf")
OUTPUT = config.get("out")
TEX = config["tex"]

PDF = "".join([PREPRINT, ".pdf"])
ALL = TEX

NAME = (
    TEX[0]["name"]
    if TEX and isinstance(TEX[0]["name"], str)
    else sys.exit("Specify project name!")
)

EXEC = (
    TEX[0]["main"]
    if TEX and isinstance(TEX[0]["main"], str)
    else sys.exit("Specify main file!")
)

DESTINATION = "release"
TMP = "archive"


def build(main=EXEC, tex=ROOT, name=PREPRINT, out=OUTPUT):
    filename, ext = os.path.splitext(main)
    maintex = "".join([tex, filename])
    cmd = [
        "latexmk",
        "-xelatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        f"-jobname={name}",
        f"-output-directory={out}",
        maintex,
    ]
    subprocess.run(cmd)


def open(preprint=PDF, build=OUTPUT):
    absolute = os.path.dirname(__file__)
    relative = "".join([build, "/", preprint])
    pdf_filename = "".join([absolute, "/", relative])
    if not os.path.exists(pdf_filename):  # check if PDF is successfully generated
        raise RuntimeError("PDF output not found")

    OS = platform.system().lower()

    # open PDF with platform-specific command
    match OS:
        case "darwin":
            subprocess.run(["open", pdf_filename])
        case "windows":
            os.startfile(pdf_filename)
        case "linux":
            subprocess.run(["xdg-open", pdf_filename])
        case _:
            raise RuntimeError(
                'Unknown operating system "{}"'.format(platform.system())
            )


extnames = [
    "aux",
    "fdb_latexmk",
    "fls",
    "lof",
    "log",
    "lol",
    "lot",
    "nav",
    "out",
    "snm",
    "gz",
    "toc",
    "xdv",
]


def clean(pdf=None):
    trash = []
    catalogue = os.walk(os.getcwd())
    for root, subdirs, files in catalogue:
        for file in files:
            extname = file.split(".")[-1]
            if extname in extnames:
                filepath = os.path.join(root, file)
                trash.append(filepath)
        if pdf in files:
            trash.append(os.path.join(root, pdf))
    for element in trash:
        os.remove(element)


def remove(preprint=PDF, build=OUTPUT, default="main.pdf"):
    preprint = "".join([build, "/", preprint])
    if os.path.exists(preprint):
        os.remove(preprint)
    clean(default)


def commit(pdfname):
    formatDate = (
        str(datetime.datetime.now().strftime(" — %b %d (%H-%Ms)"))
        .replace("/", ".")
        .replace("-", "h ")
    )
    return "".join([pdfname, formatDate])


def press(release=DESTINATION, work=NAME, preprint=PDF, build=OUTPUT, archive=TMP):
    if release is None:
        work = commit(work)
        dist = "".join([build, "/", archive])
    else:
        dist = "".join([build, "/", release])
    pdf = "".join([build, "/", preprint])
    if os.path.exists(pdf):
        sources = os.listdir(os.getcwd())
        for source in sources:
            if source.startswith(build):
                if not os.path.exists(dist):
                    os.mkdir(dist)
                filename = "".join([work, ".pdf"])
                compiled = "".join([dist, "/", filename])
                if os.path.exists(compiled):
                    os.remove(compiled)
                os.rename(pdf, compiled)
    else:
        sys.exit(">>> PDF preprint not found!")


def generate(list=ALL, release=DESTINATION):
    for tex in list:
        build(tex["main"])
        press(release, tex["name"])
        clean()


def analyze(self):
    tool = self
    list = {"linter": "pylint", "formatter": "black"}
    cmd = [list[tool]]
    cmd[0:0] = ["python"]
    cmd[1:1] = ["-m"]
    cmd.append(__file__)
    subprocess.run(cmd)


scenario = {
    "build": [build],
    "clean": [clean],
    "rm": [remove],
    "press": [press],
    "release": [build, press, clean],
    "all": [generate],
    "tmp": [build, lambda: press(None), clean],
    "open": [open],
    "dev": [build, open],
    "fmt": [lambda: analyze("formatter")],
    "lint": [lambda: analyze("linter")],
}


def run(instruction):
    if not instruction in scenario:
        sys.exit(">>> Use one argument: build, clean, release, all, tmp, open, dev")
    directives = scenario[instruction]
    for directive in directives:
        directive()


def main(args, directive="build"):
    if len(args) > 1:
        directive = args[1]
    run(directive)


if __name__ == "__main__":
    main(sys.argv)
