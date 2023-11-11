import cv2
import face_recognition as fr

# Coleta imagens do banco
imagem_banco = fr.load_image_file('testesFuncionalidades/rodrigo_lombardi_1.jpeg')
imagem_banco = cv2.cvtColor(imagem_banco, cv2.COLOR_BGR2RGB)
#imagem_entrada = fr.load_image_file('testesFuncionalidades/rodrigo_lombardi_2.jpeg')
#imagem_entrada = cv2.cvtColor(imagem_entrada, cv2.COLOR_BGR2RGB)
imagem_entrada = fr.load_image_file('testesFuncionalidades/oscar_isaac.jpeg')
imagem_entrada = cv2.cvtColor(imagem_entrada, cv2.COLOR_BGR2RGB)

# desenha o retangulo em volta da cara do individuo
face_location_imagem_banco = fr.face_locations(imagem_banco)[0]
face_location_imagem_entrada = fr.face_locations(imagem_entrada)[0]
cv2.rectangle(imagem_banco, (face_location_imagem_banco[3], face_location_imagem_banco[0]), (face_location_imagem_banco[1], face_location_imagem_banco[2]), (0, 255, 0), 2)
cv2.rectangle(imagem_entrada, (face_location_imagem_entrada[3], face_location_imagem_entrada[0]), (face_location_imagem_entrada[1], face_location_imagem_entrada[2]), (0, 255,0), 2)

# traduz para matriz a imagem para realizar a comparação
face_encoding_imagem_banco = fr.face_encodings(imagem_banco)[0]
face_encoding_imagem_entrada = fr.face_encodings(imagem_entrada)[0]

# compara as faces de cada individuo com a imagem entrada, diz a distancia entre elas e calcula a precisão de ser a mesma pessoa
mesma_pessoa = fr.compare_faces([face_encoding_imagem_banco], face_encoding_imagem_entrada, 0.5)[0]
distancia = fr.face_distance([face_encoding_imagem_banco], face_encoding_imagem_entrada)[0]
precisao = (1 - abs(distancia)) * 100

# faz um print do resultado
print(f" Comparação : {mesma_pessoa}, distancia entre imagens: {distancia}, precisão: {precisao:.2f}%")
