"""
Management команда для импорта товаров из файлов
Использование: python manage.py import_products <путь_к_файлу> [--dry-run] [--sheet <название_листа>]
"""
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from products.parsers import FileParser
from products.importers import ProductImporter


class Command(BaseCommand):
    help = 'Импортирует товары из CSV или Excel файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к файлу с товарами (CSV или Excel)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим проверки без сохранения в БД',
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=None,
            help='Название листа Excel файла (если не указано, используется первый лист)',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Минимальный вывод информации',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        dry_run = options['dry_run']
        sheet_name = options.get('sheet')
        verbose = not options.get('quiet', False)
        
        # Проверка существования файла
        if not Path(file_path).exists():
            raise CommandError(f'Файл не найден: {file_path}')
        
        # Проверка формата файла
        file_format = FileParser.detect_format(file_path)
        if not file_format:
            raise CommandError(
                f'Неподдерживаемый формат файла. '
                f'Поддерживаемые форматы: {", ".join(FileParser.SUPPORTED_FORMATS)}'
            )
        
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(f'\nИмпорт товаров из файла: {file_path}')
            )
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('Режим проверки (dry-run): данные не будут сохранены в БД\n')
                )
        
        try:
            # Парсинг файла
            if verbose:
                self.stdout.write('Парсинг файла...')
            
            if file_format == '.csv':
                parsed_data = FileParser.parse_csv(file_path)
            else:
                parsed_data = FileParser.parse_excel(file_path, sheet_name=sheet_name)
            
            if not parsed_data:
                raise CommandError('Файл не содержит данных для импорта')
            
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(f'Найдено строк: {len(parsed_data)}\n')
                )
            
            # Импорт товаров
            importer = ProductImporter(dry_run=dry_run, verbose=verbose)
            stats = importer.import_from_parsed_data(parsed_data)
            
            # Вывод результатов
            if verbose:
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('Результаты импорта:'))
                self.stdout.write(f"  Обработано: {stats['processed']}")
                self.stdout.write(
                    self.style.SUCCESS(f"  Создано: {stats['created']}")
                )
                self.stdout.write(
                    self.style.WARNING(f"  Обновлено: {stats['updated']}")
                )
                self.stdout.write(
                    self.style.ERROR(f"  Пропущено: {stats['skipped']}")
                )
                self.stdout.write(
                    self.style.ERROR(f"  Ошибок: {len(stats['errors'])}")
                )
                
                if stats['errors']:
                    self.stdout.write('\nОшибки:')
                    for error in stats['errors'][:10]:  # Показываем первые 10 ошибок
                        self.stdout.write(self.style.ERROR(f"  - {error}"))
                    if len(stats['errors']) > 10:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ... и еще {len(stats['errors']) - 10} ошибок"
                            )
                        )
                self.stdout.write('='*50 + '\n')
            else:
                # Минимальный вывод
                self.stdout.write(
                    f"Обработано: {stats['processed']}, "
                    f"Создано: {stats['created']}, "
                    f"Обновлено: {stats['updated']}, "
                    f"Ошибок: {len(stats['errors'])}"
                )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        '\nЭто был режим проверки. Для реального импорта запустите команду без --dry-run'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('\nИмпорт завершен успешно!')
                )
                
        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {str(e)}')

