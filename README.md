# KioThumb 3 — Gerador de Thumbnails Estilo Anos 90

**Gera thumbnails numeradas em lote para canais de longplay no YouTube** — com uma estética completamente inspirada nos sites pessoais do final dos anos 90, como os do GeoCities e Angelfire, e no visual do jogo **Hypnospace Outlaw**.

> **Procurando a versão completa?** O **KioThumb 2** está no mesmo perfil do GitHub e tem mais funcionalidades: assistente de extração de frames de vídeo, histórico de projetos, prévia em grade avançada e muito mais. O KioThumb 3 existe por um motivo diferente — leia abaixo.

---

## Por que esse programa existe?

O KioThumb 3 não é uma evolução do KioThumb 2. É uma versão **mais simples e com um propósito estético diferente.**

A ideia foi recriar a experiência visual dos programas e sites dos anos 90 — cores neon, fontes misturadas, texto piscante, marquee animado, contador de visitas — tudo dentro de um programa funcional de verdade. É o mesmo gerador de thumbnails, só que com a cara de um programa que poderia ter saído de dentro do **Hypnospace Outlaw**.

Se você quer o programa mais completo, vai para o KioThumb 2. Se você quer o que tem estilo, fica aqui.

---

## O que ele faz

- Gera thumbnails numeradas em lote (`#1`, `#2`, `#3`... ou o prefixo que você quiser)
- Preview em tempo real — o que você vê é o que sai
- Arraste o número e as logos direto na tela para posicionar
- Zoom e pan na imagem de fundo
- Sobreposições — adicione logos e selos em PNG com posição e tamanho independentes
- 1 imagem + quantidade 20 → 20 thumbnails com a mesma imagem
- 5 imagens + quantidade 5 → cada uma com imagem diferente
- Exporta em PNG ou JPEG em 1280×720 (padrão YouTube)
- Ctrl+V para colar prints da área de transferência
- Ctrl+Z para desfazer

## O que tem de diferente

- **Design inspirado no Hypnospace Outlaw** — paleta escura com destaques em verde, roxo e dourado queimado
- **Marquee animado** rolando no topo da janela
- **Contador de visitas** estilo mostrador digital no rodapé
- **Sons ao abrir e fechar** o programa
- **Rastro de mouse roxo** no painel de preview
- **Botão de ajuda sarcástico** — clica no `?` para ver

---

## Download

Vá em [Releases](../../releases) e baixe o `KioThumb3.exe`.

Coloque o `KioThumb3.exe` e o `icone2.png` na mesma pasta e execute. Não precisa instalar nada.

> **Sistema operacional:** Windows 10 ou superior

---

## Rodar pelo código-fonte

**Requisitos:**
- Python 3.10 ou superior
- Pillow
- psutil

```bash
py -m pip install pillow psutil
```

```bash
py kiothumb3.py
```

> O `icone2.png` precisa estar na mesma pasta.

---

## Versão completa

Para mais funcionalidades, acesse o **[KioThumb 2](https://github.com/KioHype/KioThumb-V2)** no mesmo perfil.

---

## Autor

Feito por **Daniel Perin** (ou Kiorra para os íntimos)

---

## Licença

MIT — use, modifique e distribua à vontade.
