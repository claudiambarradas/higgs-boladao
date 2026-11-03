# Exemplos para explicar o método

Os prompts abaixo ilustram cenas hipotéticas. Não são entregas prontas para qualquer vídeo. O agente precisa verificar o conteúdo real, gerar as imagens e adaptar as instruções.

## Pedido do aluno — modo manual

> Use Higgs-boladao. Neste vídeo, quero continuar sendo eu, mas com cabelo na altura dos ombros e vestido preto de paetês. Preserve meu rosto, minha pele e o ambiente. Estude o vídeo inteiro e gere as referências necessárias. Entregue as imagens já editadas, o prompt completo e o mapa de upload. Eu vou gerar o vídeo manualmente no Higgsfield.

## Pedido do aluno — cenário

> Use Higgs-boladao no modo manual. Troque a sala do vídeo por uma sala com janelão e luz lateral suave. Mantenha meu rosto, minha roupa e os movimentos. A luz em mim precisa combinar com o novo ambiente. Quero receber as imagens prontas e o prompt final.

## Pedido do aluno — automação

> Use Higgs-boladao para transformar minha roupa e cabelo como nas referências. Analise o vídeo completo, inclusive quando eu me viro para o espelho. Quero a automação no Higgsfield, preservando a proporção e o áudio. Verifique o modelo escolhido e o custo antes de gerar, depois execute dentro do limite autorizado.

## Exemplo de prompt para editar um frame principal

> Edite a imagem anexada. Preserve a fisionomia, o tom de pele, a idade aparente, o corpo, a pose, as mãos, a câmera, o enquadramento e todos os elementos do cenário. Troque apenas a roupa por um vestido preto de paetês, de alças finas, com decote reto e caimento ajustado sem mudar as proporções do corpo. Mantenha o cabelo e a maquiagem originais. Integre o brilho dos paetês à luz lateral existente, com pequenos reflexos direcionais, sombras de contato e textura de tecido. Não acrescente texto, rótulos ou molduras. Preserve a proporção e a composição da imagem original.

## Exemplo de prompt para editar outro ângulo

> A primeira imagem é o frame original de perfil e define a pose, a câmera, a composição e a iluminação. A segunda imagem é a âncora do novo visual e define o vestido preto de paetês já aprovado. Edite a primeira imagem aplicando o mesmo vestido, mantendo alças, recorte, cor, material e caimento coerentes com a segunda. Não copie a pose frontal da âncora. Preserve identidade, cabelo, pele, mãos e ambiente do frame de perfil. Ajuste as sombras e os reflexos dos paetês à luz deste ângulo. Não adicione texto nem altere o enquadramento.

## Exemplo de prompt final com três referências reais

Somente usar a estrutura abaixo se as três imagens tiverem sido efetivamente geradas e corresponderem a frente, perfil e espelho do vídeo:

```text
Edite @video1 para aplicar à mulher o vestido preto de paetês mostrado
em @imagem1, preservando sua identidade, seu rosto, tom de pele, cabelo,
maquiagem e proporções corporais. @imagem1 define o visual principal;
@imagem2 mostra o mesmo vestido no perfil; @imagem3 mostra a integração
do visual quando a mulher aparece diante do espelho, incluindo o reflexo.

Use @video1 como origem da sequência temporal: mantenha movimentos,
gestos, expressões, direção do olhar, ritmo, sincronização labial,
trajetória da câmera, enquadramento e duração. Não invente novas ações.
Use as três referências para manter o mesmo modelo de vestido, alças,
decote, cor e material em todos os ângulos, sem trocar o penteado.

Preserve o cenário e os objetos de @video1. Adapte o brilho dos paetês,
as dobras, as sombras de contato e as oclusões ao movimento e à luz de
cada momento. Quando houver reflexo, mostre o mesmo vestido e a mesma
pessoa na perspectiva correta do espelho, de modo coerente com @imagem3.
Mantenha as mãos e os objetos segurados íntegros. Não adicione cortes,
zoom, câmera lenta, legendas, textos, marcas ou elementos extras.
```

A manutenção do áudio deve também ser configurada e conferida conforme a operação disponível. O prompt por si só não garante que a ferramenta preservará a faixa sonora. O agente deve entregar os parâmetros verificados junto com as imagens.

## O que não é aceitável como entrega manual

“Use uma imagem de frente e uma de costas” sem produzir os arquivos; um ZIP que só contém prompts; uma colagem usada no lugar de imagens individuais; referência no texto sem arquivo correspondente; ou qualquer afirmação de que o pacote está pronto enquanto falta gerar ou disponibilizar as imagens.
