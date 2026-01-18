# Stage 1: Збірка залежностей у builder-стадії
FROM python:3.12-slim AS builder

# Встановлюємо робочу директорію та залежності
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Копіюємо тільки необхідні файли для зменшення розміру образу
FROM python:3.12-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо встановлені залежності з builder-стадії
COPY --from=builder /root/.local /root/.local

# Копіюємо код проекту
COPY . .

# Додаємо шлях до Python-залежностей
ENV PATH=/root/.local/bin:$PATH

# Встановлюємо проект у режимі редагування
RUN pip install -e .

# Вказуємо команду за замовчуванням
ENTRYPOINT ["python", "-m", "ai_slop_gate.cli.main"]

# Команда за замовчуванням для показу довідки
CMD ["--help"]

# Перевірка здоров'я контейнера
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import ai_slop_gate; print('OK')" || exit 1
