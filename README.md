# PDF para Markdown (Windows)

Aplicativo desktop gratuito para converter arquivos PDF em Markdown localmente no Windows 10 x64. O projeto é independente do conversor de sites e ainda não foi publicado no GitHub.

## O que faz

- Converte texto e estrutura de PDFs usando [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html), com suporte a títulos, listas e tabelas detectadas.
- Opcionalmente aplica OCR local em páginas digitalizadas. OCR requer dados de idioma Tesseract instalados; veja **OCR e tamanho**.
- Salva um arquivo `.md` ao lado do PDF. Se o destino existir, a conversão para sem alterar o arquivo existente.
- Mostra estado, progresso e erros em uma janela gráfica. Também pode ser aberto pelo menu de contexto do Explorador.
- O PDF não é enviado a serviços externos. O modo sem OCR funciona totalmente offline.

## Requisitos

- Windows 10 ou 11, 64 bits.
- Para compilar: Python 3.10 de 64 bits, pip e Inno Setup 6. O build cria `.venv` e instala PyMuPDF4LLM 0.3.x e PyInstaller.
- A distribuição instalada é autocontida e não requer Python no computador de destino.

## Instalação para desenvolvimento

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
```

## Compilar

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

O executável será criado em `dist\PDF para Markdown\PDF para Markdown.exe`. O workflow também compila o instalador pelo GitHub Actions. Para uma compilação local, depois de executar o build, rode `powershell -ExecutionPolicy Bypass -File .\compile-installer.ps1`; o script localiza o Inno Setup 6 e salva o setup em `dist-installer`. O instalador registra a opção de menu para o usuário atual (`HKCU`) e o desinstalador remove essa opção.

## Obter o instalador pelo GitHub (sem terminal)

Para preparar o repositório pelo navegador:

1. Entre no GitHub e clique no botão **+** no alto da página; escolha **New repository**.
2. Dê um nome ao repositório, escolha **Public**, marque **Add a README file** e clique em **Create repository**.
3. Extraia `PDF-para-Markdown-source-0.1.0.zip` no Explorador de Arquivos.
4. Na página do repositório, clique em **Add file** e depois em **Upload files**.
5. Arraste os arquivos e pastas extraídos para a página. Confirme que a pasta `.github` e seu conteúdo também foram enviados; ela contém o workflow que compila o instalador.
6. Clique em **Commit changes** para enviar os arquivos.

Depois do envio, o GitHub inicia o build:

1. Clique em **Actions** no repositório. Se o GitHub pedir, confirme que deseja habilitar Actions.
2. Aguarde o workflow **Build Windows installer** terminar. Se não iniciar automaticamente, selecione esse workflow, clique em **Run workflow** e confirme.
3. Clique na execução concluída e, na seção **Artifacts** ao final da página, baixe `PDF-para-Markdown-Setup-Windows-x64`.
4. No Explorador, abra o ZIP baixado, extraia o instalador e dê dois cliques em `PDF-para-Markdown-Setup-0.1.0-x64.exe`.

O artifact fica disponível por 14 dias. O workflow não publica uma Release nem envia o instalador para outro serviço. Para baixar um artifact, é necessário estar conectado a uma conta GitHub com acesso de leitura ao repositório, inclusive quando ele é público ([documentação do GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)).

O instalador ainda não é assinado digitalmente. Na primeira execução, o Windows pode exibir uma confirmação do SmartScreen porque o projeto não tem um certificado de assinatura de código.

## Uso

Abra o aplicativo e selecione um PDF, ou clique com o botão direito em um PDF no Explorador e escolha **Converter para Markdown**. Uma conversão concluída cria `nome-do-arquivo.md` na mesma pasta. Se esse nome já estiver ocupado, mova o Markdown existente ou renomeie/mova o PDF; o arquivo existente nunca é sobrescrito. PDFs protegidos por senha precisam ser desbloqueados antes.

O menu de contexto é instalado por usuário, sem exigir privilégios de administrador. A entrada chama o executável passando o caminho do PDF como argumento; ela não abre terminal.

## OCR e tamanho

O OCR é opcional. O PyMuPDF4LLM usa o mecanismo local integrado ao PyMuPDF e precisa dos arquivos `tessdata` de Tesseract para o idioma solicitado. São dados de modelo, não um serviço online. Inglês usa `eng.traineddata`; português usa `por.traineddata`. Os tamanhos variam por versão e tipo de modelo; na variante rápida, os arquivos atuais têm cerca de 3,92 MB (inglês) e 1,89 MB (português). Para melhor precisão, `tessdata_best` é consideravelmente maior e mais lenta. Baixe os dados do idioma desejado, extraia-os para uma pasta `tessdata` e selecione essa pasta no campo **Pasta tessdata** do aplicativo. O código de idioma deve corresponder ao arquivo instalado (por exemplo, `por+eng` precisa dos dois arquivos). Primeiro uso de OCR exige a obtenção desses arquivos; sem eles, conversões sem OCR continuam disponíveis. O aplicativo não baixa modelos silenciosamente.

O binário PyInstaller inclui o runtime Python e bibliotecas de PDF, por isso será substancialmente maior que o script-fonte; o tamanho final deve ser lido do artefato compilado. Os dados OCR ficam separados e só são necessários se a opção OCR for usada.

## Limitações

PDF é um formato de apresentação, não uma descrição semântica. Colunas, títulos, listas e tabelas dependem de heurísticas e podem precisar de revisão manual. OCR erra em digitalizações inclinadas, baixa resolução, escrita manual e idiomas não instalados. Fórmulas, notas de rodapé, gráficos e layouts complexos podem perder fidelidade. A saída contém texto e estrutura reconhecidos; não promete reprodução visual nem preservação de imagens. PDFs criptografados, danificados ou muito grandes podem não ser processados.

## Licenças e transparência

O código deste projeto está sob MIT (veja `LICENSE`). PyMuPDF/PyMuPDF4LLM são distribuídos sob AGPL-3.0 ou licença comercial; a forma de distribuição do aplicativo compilado deve respeitar a licença escolhida. Consulte as licenças upstream antes de publicar. Dados Tesseract têm licenciamento próprio (Apache-2.0). Nenhuma credencial ou segredo é necessário.

## Verificações

O script de build valida a arquitetura do Python, instala dependências declaradas, compila o executável e verifica a presença do artefato. Verificações do ambiente desta tarefa estão anotadas em `VERIFICATION.md`.

