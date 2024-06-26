document.addEventListener('DOMContentLoaded', function () {
    const progressCircle = document.querySelector('.progress-ring__circle');
    const progressText = document.querySelector('.progress-text');
    const progressCircleContainer = document.querySelector('.progress-circle');
    const percentage = progressCircleContainer.getAttribute('data-percentage');
    
    const radius = progressCircle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;

    progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    progressCircle.style.strokeDashoffset = circumference;

    function setProgress(percent) {
        const offset = circumference - (percent / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
        progressText.textContent = `${percent}%`;
    }

    setProgress(percentage);  // Utilise le pourcentage de l'attribut data-percentage
});
