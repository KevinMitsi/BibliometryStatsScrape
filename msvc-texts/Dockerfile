# ==============================================================================
# Etapa 1: Builder - Compila la aplicación y sus dependencias
# ==============================================================================
FROM maven:3.8.5-openjdk-17 AS builder

WORKDIR /app

# Copia todo el proyecto, no solo pom.xml y src
COPY . .

# Agrega paso de debugging para ver qué archivos hay antes de construir
RUN ls -la

# Ejecuta el build con salida detallada para ver cualquier error
RUN mvn clean package -DskipTests=true -e

# Verifiquemos que se creó el JAR
RUN ls -la target/

# ==============================================================================
# Etapa 2: Runtime
# ==============================================================================
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copia el JAR específico por nombre o de manera más flexible con comodín
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8003

# Usa el nombre genérico que asignamos en la fase de copia
ENTRYPOINT ["java", "-jar", "app.jar"]