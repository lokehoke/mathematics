"""Restore named LaTeX targets lost by PDF optimization without changing pages."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, TextStringObject


def restore_destinations(original_path, reading_path):
    original = PdfReader(original_path)
    reading = PdfReader(reading_path)
    assert len(original.pages) == len(reading.pages)
    missing = set(original.named_destinations) - set(reading.named_destinations)
    if not missing:
        return 0
    writer = PdfWriter()
    writer.clone_document_from_reader(reading)
    for name in sorted(missing):
        destination = original.named_destinations[name]
        index = original.get_destination_page_number(destination)
        assert index is not None
        array = ArrayObject([writer.pages[index].indirect_reference])
        array.extend(destination.dest_array[1:])
        writer.add_named_destination_array(TextStringObject(name), array)
    path = Path(reading_path)
    temporary = path.with_name(path.stem + ".navigation.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)
    temporary.replace(path)
    restored = PdfReader(path)
    assert set(restored.named_destinations) == set(original.named_destinations)
    for name, destination in original.named_destinations.items():
        assert original.get_destination_page_number(destination) == restored.get_destination_page_number(restored.named_destinations[name])
    return len(missing)
