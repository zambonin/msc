SRC_FILES = $(wildcard *.tex)
SLIDE_FILES = $(wildcard slides/*.tex)
CHART_FILES = $(wildcard charts/**/*.tex)
OUTPUT = $(SRC_FILES:.tex=.pdf)

all: $(OUTPUT)

$(OUTPUT): $(CHART_FILES:.tex=.pdf)

slides: $(SLIDE_FILES:.tex=.pdf)

charts/diffusion/cdf-plot.tex charts/diffusion/qq-plot.tex: \
	charts/diffusion/t65536-fix.txt charts/diffusion/t65536-nofix.txt
charts/diffusion/t65536-fix.txt: /usr/bin/sage
	sage charts/diffusion/count-rankit.sage 65536 fix >| $@
charts/diffusion/t65536-nofix.txt: /usr/bin/sage
	sage charts/diffusion/count-rankit.sage 65536 nofix >| $@

charts/inv-prob/inv-prob.tex charts/inv-prob-zoom.tex: charts/inv-prob/prob.txt
charts/inv-prob/prob.txt: /usr/bin/sage
	sage charts/inv-prob/sing-mat-chance.sage 256 56 90 >| $@

charts/measure-diff/std-diff-n42.tex: charts/measure-diff/q256-t512-n42.txt
charts/measure-diff/q256-t512-n42.txt: /usr/bin/sage
	sage charts/measure-diff/3d-view-std-comp.sage 256 512 42 >| $@
charts/measure-diff/std-diff-n90.tex: charts/measure-diff/q256-t512-n90.txt
charts/measure-diff/q256-t512-n90.txt: /usr/bin/sage
	sage charts/measure-diff/3d-view-std-comp.sage 256 512 90 >| $@

ufsc-thesis-rn46-2019/ufsc-thesis-rn46-2019.cls:
	git submodule update --init $(dir $@)

%.pdf: %.tex
	latexmk -f -interaction=nonstopmode -shell-escape -pdf -use-make -cd $<

clean:
	latexmk -pdf -cd -C $(SRC_FILES) $(CHART_FILES)
	$(RM) slides/*.bbl slides/*.nav slides/*.snm main.bbl
	find charts/ -type f -iname '*.pgf*' -delete

clean-data:
	find charts/ -type f -iname '*.txt' -delete
