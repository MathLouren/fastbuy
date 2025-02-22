function verificarSenhas() {
        const senha = document.getElementById("password").value;
        const confirmarSenha = document.getElementById("confirm_password").value;

        if (senha !== confirmarSenha) {
            alert("As senhas não coincidem. Tente novamente.");
            return false;
        }
        return true;
    }

document.getElementById('menu-toggle').addEventListener('click', function() {
        const menu = document.getElementById('menu');
        menu.classList.toggle('show');
    });


window.addEventListener('DOMContentLoaded', function () {
        const messageContainer = document.getElementById('message-container');
        if (messageContainer) {

            setTimeout(function () {
                messageContainer.style.display = 'none';
            }, 3000);
        }
    });

    function verificarSenhas() {
        var senha = document.getElementById("password").value;
        var confirmarSenha = document.getElementById("confirm_password").value;

        if (senha !== confirmarSenha) {
            alert("As senhas não coincidem. Por favor, verifique e tente novamente.");
            return false;
        }
        return true;
    }


    function formatarTelefone(input) {
        let valor = input.value.replace(/\D/g, '');
        if (valor.length <= 2) {
            input.value = '(' + valor;
        } else if (valor.length <= 7) {
            input.value = '(' + valor.substring(0, 2) + ') ' + valor.substring(2);
        } else {
            input.value = '(' + valor.substring(0, 2) + ') ' + valor.substring(2, 7) + '-' + valor.substring(7, 11);
        }
    }

function formatarPreco(input) {
        let valor = input.value.replace(/\D/g, "");
        if (valor.length === 0) {
            input.value = "";
            return;
        }
        valor = (parseFloat(valor) / 100).toFixed(2);
        valor = valor.replace(".", ",");
        valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        input.value = "R$ " + valor;
    }


document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".user_infos li a");

    const setActiveItem = (activeLink) => {
        links.forEach(link => link.classList.remove("active"));
        activeLink.classList.add("active");
    };

    links.forEach(link => {
        link.addEventListener("click", () => setActiveItem(link));
    });

    const currentUrl = window.location.href;
    links.forEach(link => {
        if (currentUrl.includes(link.querySelector("a").getAttribute("href"))) {
            setActiveItem(link);
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".user_infos a");
    const conteudoDinamico = document.getElementById("conteudo-dinamico");

    const carregarConteudo = async (pagina) => {
        try {
            const response = await fetch(`/dashboard/${pagina}`);
            if (!response.ok) throw new Error("Erro ao carregar o conteúdo");

            const html = await response.text();
            conteudoDinamico.innerHTML = html;
        } catch (error) {
            console.error("Erro:", error);
            conteudoDinamico.innerHTML = "<p>Erro ao carregar o conteúdo.</p>";
        }
    };

    links.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            links.forEach(link => link.classList.remove("active"));

            link.classList.add("active");

            const pagina = link.getAttribute("data-page");
            carregarConteudo(pagina);
        });
    });

    carregarConteudo("perfil");
});

document.addEventListener("DOMContentLoaded", () => {
    const bioTextarea = document.getElementById("bio");
    const bioCounter = document.getElementById("bio-counter");

    if (bioTextarea && bioCounter) {
        bioTextarea.addEventListener("input", () => {
            const length = bioTextarea.value.length;
            bioCounter.textContent = `${length}/500 caracteres`;
        });

        bioCounter.textContent = `${bioTextarea.value.length}/500 caracteres`;
    }
});



document.querySelector('.pic_edit').addEventListener('click', function() {
    document.getElementById('imagem').click();
});

document.getElementById('imagem').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('.pic_edit img').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});
