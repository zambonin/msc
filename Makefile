SRC_FILES = $(wildcard slides/*.tex)
OUTPUT = $(SRC_FILES:.tex=.pdf)

all: $(OUTPUT)

%.pdf: %.tex
	latexmk -f -interaction=nonstopmode -shell-escape -pdf -use-make -cd $<

clean:
	latexmk -pdf -cd -C $(SRC_FILES)
	$(RM) slides/*.bbl slides/*.nav slides/*.snm
