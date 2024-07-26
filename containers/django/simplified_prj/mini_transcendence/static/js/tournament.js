// verifier que les alias des player sont tous remplis (non null) et uniques
document.getElementById('matchForm').addEventListener('submit', function(event) {
    // selectioner tous les inputs du type texte qui servent pour mettre les alias
    const players = document.querySelectorAll('input[type="text"][name="player"]');
    let allFilled = true;
    let aliases = [];
    players.forEach(player => {
        const playerAlias = player.value.trim();
        if (playerAlias === '') {
            allFilled = false;
        } else {
            aliases.push(playerAlias);
        }
    });
    if (!allFilled) {
        alert('Please fill in all aliases.');
        event.preventDefault();
        return;
    }
    // filter permet d'obtenir la sous-liste d'aliases, avec que des dupliquee 
    // si la premiere occurence d'un alias est different de
    // l'indice recent, ca signifie qu'on a un duplicate, 
    // et donc la liste duplicates sera non vide
    let duplicates = aliases.filter((name, index, self) => self.indexOf(name) !== index);
    if (duplicates.length > 0) {
        alert('Duplicate player names are not allowed: ' + duplicates.join(', '));
        event.preventDefault();
    }
});
