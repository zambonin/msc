#!/usr/bin/env sh

INPUT="${1:-main.tex}"
PAGES="$(pdfinfo "${INPUT/tex/pdf}" | awk '/Pages/ { print $(NF) }')"

DATA="$(awk '
  function split_names(header1, header2, name) {
    len = split(name, array, " ")
    printf header1
    for (i = 1; i < len - 1; ++i) {
      printf "%s ", array[i]
    }
    printf "%s&%s%s&", array[len - 1], header2, array[len]
  }

  BEGIN { FS = "{|} ?|\\. ?|, " }

  /autor{/ { autor = $2 }
  /titulo{/ { titulo = $2 }
  /centro{/ { centro = $2 }
  /data{/ { ano = $2 }
  /programa{/ { sub("Programa de Pós-Graduação em ", "", $2); programa = $2 }
  { t = ($0 == "\\\\tese") }
  /\\orientador[a]?{/ { orientador = $3 }
  /\\coorientador[a]?{/ { coorientador = $3 }
  /-chave:/ { assunto2 = $3; assunto3 = $4; assunto4 = $5; assunto5 = $6 }

  END {
    split_names("nome=", "sobrenome=", autor)
    split_names("nome_ori=", "sobrenome_ori=", orientador)
    split_names("nome_coori=", "sobrenome_coori=", coorientador)

    printf "titulo=%s&trabalho=%s&programa=%s&centro=%s&ano=%s&",
        titulo, t ? "tese" : "dissertacao", programa, centro, ano
    printf "assunto2=%s&assunto3=%s&assunto4=%s&assunto5=%s",
        assunto2, assunto3, assunto4, assunto5
  }
' $INPUT)"

curl -o index-card.pdf -d "autor=autor1" -d "formatoPagina=a4" \
  -d "pags=$PAGES" -d "$DATA" http://ficha.bu.ufsc.br/pdf.php
