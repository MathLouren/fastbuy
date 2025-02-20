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


