function verificarSenhas() {
        const senha = document.getElementById("password").value;
        const confirmarSenha = document.getElementById("confirm_password").value;

        if (senha !== confirmarSenha) {
            alert("As senhas não coincidem. Tente novamente.");
            return false;
        }
        return true;
    }



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
        let valor = input.value.replace(/\D/g, ""); // Remove tudo que não for número
        if (valor.length === 0) {
            input.value = ""; // Se estiver vazio, limpa o campo
            return;
        }

        valor = (parseFloat(valor) / 100).toFixed(2); // Divide por 100 para manter as casas decimais corretamente
        valor = valor.replace(".", ","); // Converte para formato brasileiro

        // Adiciona separadores de milhar
        valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

        input.value = "R$ " + valor; // Adiciona o símbolo R$
    }

document.getElementById("preco").addEventListener("input", function(e) {
    let value = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número
    value = (value / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    e.target.value = value;
});

