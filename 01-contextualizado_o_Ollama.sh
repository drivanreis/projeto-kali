#!/bin/bash
# /01-contextualizar_o_ollama.sh

# nome do arquivo de saída
OUTPUT_FILE="contexto_projeto.txt"

echo "=== gerando contexto global do projeto ===" > $OUTPUT_FILE
echo "data de geração: $(date)" >> $OUTPUT_FILE
echo "----------------------------------------" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "=== estrutura do diretório ===" >> $OUTPUT_FILE
if command -v tree &> /dev/null; then
    tree -I "node_modules|__pycache__|\.git|\.venv|venv" >> $OUTPUT_FILE
else
    find . -maxdepth 3 -not -path '*/.*' -not -path '*node_modules*' -not -path '*__pycache__*' -not -path '*venv*' >> $OUTPUT_FILE
fi
echo "----------------------------------------" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# varre arquivos relevantes do backend e frontend
find . -type f \( -name "*.py" -o -name "*.json" -o -name "*.jsonl" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.md" \) \
-not -path '*/.*' \
-not -path '*node_modules*' \
-not -path '*__pycache__*' \
-not -path '*venv*' \
-not -path '*/dist/*' \
-not -path "*$OUTPUT_FILE*" \
-not -path "*contextualizado_o_Ollama.sh*" | while read -r file; do
    echo "========================================" >> $OUTPUT_FILE
    echo "arquivo: $file" >> $OUTPUT_FILE
    echo "========================================" >> $OUTPUT_FILE
    cat "$file" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
done

echo "pronto! o arquivo '$OUTPUT_FILE' foi gerado com todo o contexto do projeto."