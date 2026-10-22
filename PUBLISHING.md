# Publicação no GitHub

## Pela interface web

1. Crie um repositório vazio no GitHub, sem adicionar README, `.gitignore` ou licença.
2. Extraia este pacote em seu computador.
3. Na página do novo repositório, escolha **uploading an existing file**.
4. Envie todo o conteúdo da pasta `gmcr-optimal-preference-adjustment` e confirme o commit.

Para preservar melhor o histórico, prefira o método por linha de comando.

## Pela linha de comando

Dentro da pasta do projeto:

```bash
git init
git add .
git commit -m "Initial reproducible research repository"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
git push -u origin main
```

Com o GitHub CLI autenticado, também é possível criar e publicar de uma vez:

```bash
gh repo create NOME-DO-REPOSITORIO --public --source=. --remote=origin --push
```

Antes da publicação, escolha uma licença apropriada para o código. Nenhuma licença foi imposta automaticamente neste pacote.
