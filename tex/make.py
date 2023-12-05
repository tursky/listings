import os
import platform
import subprocess
import sys
import json
import datetime


def read(filename):
    with open(filename, "r", encoding="utf=8") as file:
        return json.load(file)


config = read("setup.json")


APPLICATION = config.get("src")
PRINTNAME = config.get("pdfprint")
OUTPUT = config.get("dist")
PROJECTS = config["works"]

PDF = "".join([PRINTNAME, ".pdf"])
ALL = PROJECTS

NAME = (
    PROJECTS[0]["name"]
    if PROJECTS and isinstance(PROJECTS[0]["name"], str)
    else sys.exit("Specify your TEX-sources!")
)

EXEC = (
    PROJECTS[0]["exec"]
    if PROJECTS and isinstance(PROJECTS[0]["exec"], str)
    else sys.exit("Specify your TEX-execute main file!")
)

DIST = "release"
TEMPORARY = "archive"


def build(main=EXEC, tex=APPLICATION, preprint=PRINTNAME, build=OUTPUT):
    filename, ext = os.path.splitext(main)
    executefile = "".join([tex, "/", filename])
    cmd = [
        "latexmk",
        "-xelatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        f"-jobname={preprint}",
        f"-output-directory={build}",
        executefile,
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
        str(datetime.datetime.now().strftime(" ~ %b %d (%H-%Ms)"))
        .replace("/", ".")
        .replace("-", "h ")
    )
    return "".join([pdfname, formatDate])


def press(release=DIST, doc=NAME, preprint=PDF, build=OUTPUT, archive=TEMPORARY):
    if release is None:
        doc = commit(doc)
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
                filename = "".join([doc, ".pdf"])
                compiled = "".join([dist, "/", filename])
                if os.path.exists(compiled):
                    os.remove(compiled)
                os.rename(pdf, compiled)
    else:
        sys.exit(">>> PDF preprint not found!")


def generate(list=ALL, release=DIST):
    for tex in list:
        build(tex["exec"])
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
    "archive": [build, lambda: press(None), clean],
    "open": [open],
    "dev": [build, open],
    "lint": [lambda: analyze("linter")],
    "fmt": [lambda: analyze("formatter")],
}


def run(instruction):
    if not instruction in scenario:
        sys.exit(">>> Use one argument: build, clean, release, all, archive, open, dev")
    directives = scenario[instruction]
    for directive in directives:
        directive()


def main(args, directive="build"):
    if len(args) > 1:
        directive = args[1]
    run(directive)


if __name__ == "__main__":
    main(sys.argv)
