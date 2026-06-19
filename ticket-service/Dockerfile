# ==========================================
# Stage 1: Build the Application using Maven & JDK 21
# ==========================================
FROM maven:3.9.6-eclipse-temurin-21-alpine AS builder

WORKDIR /app

# نسخ ملف الـ pom.xml لتحميل الـ Dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# نسخ الكود المصدري وعمل البناء
COPY src ./src
RUN mvn clean package -DskipTests

# ==========================================
# Stage 2: Production Runtime with JRE 21
# ==========================================
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# إنشاء مستخدم غير جذر لتعزيز الأمان DevSecOps
RUN addgroup -S ticketgroup && adduser -S ticketuser -G ticketgroup

# نسخ ملف الـ jar المبني من المرحلة الأولى
COPY --from=builder /app/target/ticket-service-0.0.1-SNAPSHOT.jar app.jar

RUN chown -R ticketuser:ticketgroup /app
USER ticketuser

EXPOSE 8081

# تشغيل التطبيق مع الـ Optimization الخاصة بـ Java 21
ENTRYPOINT ["java", "-XX:+UseG1GC", "-jar", "app.jar"]
