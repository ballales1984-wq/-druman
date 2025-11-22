# Contribuire a DrumMan

Grazie per il tuo interesse a contribuire a DrumMan! 🎉

## Come Contribuire

### Segnalare Bug

Se trovi un bug, apri una [GitHub Issue](https://github.com/tuonome/druman/issues) con:
- Descrizione chiara del problema
- Passi per riprodurre
- Comportamento atteso vs. comportamento reale
- Screenshot se applicabile
- Informazioni sistema (OS, Python version, etc.)

### Proporre Funzionalità

Apri una [GitHub Issue](https://github.com/tuonome/druman/issues) con:
- Descrizione della funzionalità
- Caso d'uso
- Esempi se applicabile

### Pull Requests

1. **Fork** il repository
2. Crea un **branch** per la tua feature:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** le modifiche:
   ```bash
   git commit -m 'Add AmazingFeature'
   ```
4. **Push** al branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Apri una **Pull Request**

## Linee Guida del Codice

### Python Style

- Segui **PEP 8**
- Usa **type hints** quando possibile
- Massima lunghezza riga: **100 caratteri**
- Usa **docstring** per funzioni e classi

### Struttura Codice

```python
"""
Breve descrizione del modulo.
"""
import standard_library
import third_party
import local_modules

class MyClass:
    """Descrizione della classe."""
    
    def __init__(self, param: str):
        """Inizializza la classe.
        
        Args:
            param: Descrizione parametro
        """
        self.param = param
    
    def method(self) -> bool:
        """Descrizione metodo.
        
        Returns:
            True se successo
        """
        return True
```

### Test

- Testa le modifiche con `test_components.py`
- Verifica che non ci siano errori di linting
- Assicurati che il codice funzioni su Windows, Linux e macOS

### Documentazione

- Aggiorna il README se aggiungi funzionalità
- Aggiungi commenti per codice complesso
- Documenta API pubbliche

## Aree di Contribuzione

### Priorità Alta
- 🐛 Bug fixes
- 📚 Documentazione
- ⚡ Performance improvements
- 🧪 Test coverage

### Priorità Media
- 🎨 UI/UX improvements
- 🔊 Audio quality improvements
- 🎯 Tracking accuracy
- 📱 Mobile support

### Priorità Bassa
- 🌐 Localization
- 🎮 Game modes
- 🤖 AI features
- 📊 Analytics

## Domande?

Apri una [GitHub Discussion](https://github.com/tuonome/druman/discussions) o contatta i maintainer.

Grazie per il tuo contributo! 🙏

