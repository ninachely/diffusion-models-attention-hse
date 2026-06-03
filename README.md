# Анализ механизма внимания в диффузионных моделях

**Трек**: Research

**Команда**: Нина Челышева

**Куратор**: Ева Неудачина

## Цель работы

Исследовать свойства и роль механизма внимания в text2image диффузионной модели FLUX: выделить «vital» слои/головы, проследить динамику по таймстепам, применить для одной из downstream задач (редактирование изображений, ускорение генерации и т.д.).

## План работы

1. Знакомство с куратором, постановка и уточнение задачи, план на год.
2. Изучение статей по смежным областям: attention interpretation, caching в диффузии, XAI/SAE/probing.
3. Фиксация набора текстовых промптов для дальнейших экспериментов.
4. Изучение архитектуры text2image диффузионной модели FLUX.
5. Модификация кода модели FLUX: forward хуки Q/K/V и карт внимания по слоям/головам на каждом временном шаге.
6. Анализ по временным шагам: энтропия/стабильность, кластеризация голов; связь с текстовыми токенами и визуальными признаками; проберы/SAE.
7. Выдвижение гипотез по улучшению существующих методов в downstream задачах.
8. Улучшение одного из существующих методов в downstream задачах.
9. Написание Telegram-бота для генерации изображений с помощью FLUX c визуализацией карт внимания по токенам/слоям/временным шагам.
10. Доработка задачи: улучшение сервисной части по обратной связи от команды курса П.Р.; завершение research-части и подведение итогов по проведенным исследованиям.

## Итоговая постановка

В работе исследуется, можно ли использовать внутреннюю структуру attention в FLUX для более контролируемого редактирования изображений. Основная гипотеза: не все attention-головы одинаково полезны для переноса визуальной структуры, поэтому вмешательство только в устойчивые `vital`-головы должно быть мягче, чем полный shared-attention по всем головам.

В ноутбуках реализованы:

1. Сбор attention-статистик по слоям, головам и таймстепам.
2. Выделение `vital`-голов по entropy/stability.
3. Сравнение `flux_plain`, `flux_shared_all_heads`, `flux_shared_vital_heads` и baseline.
4. Логирование финального эксперимента в MLflow.
5. Регистрация финальной версии модели с alias/tag `PRD`.
6. Error analysis и robustness-анализ.
7. Демонстрационная загрузка `PRD`-модели без повторного обучения.

## Файлы

- `ML_Experiments.ipynb` — исследование attention и первичные shared-attention абляции.
- `DL_Experiments.ipynb` — финальный экспериментальный pipeline, MLflow logging, Model Registry, error analysis, robustness.
- `DL_Demonstration.ipynb` — загрузка `PRD`-модели из MLflow и тестовый inference.

## Запуск Checkpoint 7

В cloud-среде без Docker MLflow можно поднять локально:

```bash
conda activate nyuchelysheva_rf_inversion
cd /home/jovyan/nyuchelysheva/diffusion-models-attention-hse
mkdir -p mlflow_local/artifacts

nohup mlflow server \
  --backend-store-uri sqlite:////home/jovyan/nyuchelysheva/diffusion-models-attention-hse/mlflow_local/mlflow.db \
  --default-artifact-root file:///home/jovyan/nyuchelysheva/diffusion-models-attention-hse/mlflow_local/artifacts \
  --host 127.0.0.1 \
  --port 5000 \
  > mlflow_local/mlflow_server.log 2>&1 &
```

Проверка:

```bash
curl -I http://127.0.0.1:5000
```

После этого запускается `DL_Experiments.ipynb` целиком, затем `DL_Demonstration.ipynb`.
