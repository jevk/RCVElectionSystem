class Candidate {
    constructor(name) {
        this.name = name;
        this.rank = 0;
    }

    getRank() {
        return this.rank;
    }

    getName() {
        return this.name;
    }

    setRank(rank) {
        this.rank = rank;
    }

    setName(name) {
        this.name = name;
    }
}

function allRanksAboveZero(objects) {
    for (let i = 0; i < objects.length; i++) {
        if (objects[i].getRank() === 0) {
            return false;
        }
    }
    return true;
}

function sendResults() {
    const candidates = [];
    const entries = document.getElementsByName("candidate-name");
    entries.forEach((c) => {
        const name = c.textContent;
        const candidate = new Candidate(name);

        for (let i = 1; i <= entries.length; i++) {
            const voteNumber = name + i;
            const vote = document.getElementById(voteNumber);

            if (vote.checked) {
                candidate.setRank(i);
                break;
            } else {
                candidate.setRank(0);
            }
        }
        candidates.push(candidate);
    });
    if (allRanksAboveZero(candidates)) {
        console.log(candidates);
        return candidates;
    } else {
        alert("Invalid Vote!\n \nPlease rank all candidates, and make sure no two candidates have the same rank.");
    }
}