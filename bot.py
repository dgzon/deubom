from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging

# Configurações do bot
TOKEN = "7502354618:AAEXahImYsbLthBeLVMOhQMscx7mHs_dciE"
CHAVE_PIX = "gabrielahotandrade@gmail.com"
LINK_ACESSO = "https://t.me/+6oWwkp5kQ61jODRh"
ADMIN_ID = 7258828491  # 🔴 SEU ID DE ADMINISTRADOR

# Configuração do logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Dicionário para armazenar usuários pendentes de aprovação
usuarios_pendentes = {}

# Dicionário para armazenar quantidade de vendas
relatorio_vendas = {"7 dias": 0, "15 dias": 0, "30 dias": 0}

async def start(update: Update, context: CallbackContext) -> None:
    """Envia a mensagem inicial com os planos disponíveis"""
    mensagem = (
        "🔥 Bem-vindo ao *Grupo VIP*! Aqui estão os planos disponíveis:\n\n"
        "💎 *Plano 1 - Acesso por 7 dias* ➝ R$ 29,90\n"
        "💎 *Plano 2 - Acesso por 15 dias* ➝ R$ 49,90\n"
        "💎 *Plano 3 - Acesso por 30 dias* ➝ R$ 79,90\n\n"
        "Clique abaixo para escolher seu plano e realizar o pagamento! 👇"
    )

    keyboard = [
        [InlineKeyboardButton("💰 Pagar 7 dias - R$ 29,90", callback_data="plano_7")],
        [InlineKeyboardButton("💰 Pagar 15 dias - R$ 49,90", callback_data="plano_15")],
        [InlineKeyboardButton("💰 Pagar 30 dias - R$ 79,90", callback_data="plano_30")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(mensagem, reply_markup=reply_markup, parse_mode="Markdown")

async def selecionar_plano(update: Update, context: CallbackContext) -> None:
    """Envia os dados para pagamento após o usuário selecionar um plano"""
    query = update.callback_query
    await query.answer()

    plano = query.data.split("_")[1]
    if plano == "7":
        valor = "R$ 29,90"
        nome_plano = "7 dias"
    elif plano == "15":
        valor = "R$ 49,90"
        nome_plano = "15 dias"
    else:
        valor = "R$ 79,90"
        nome_plano = "30 dias"

    mensagem = (
        f"💰 Você escolheu o plano de {nome_plano} por {valor}.\n\n"
        "📌 Realize o pagamento via *Pix* usando a chave abaixo:\n\n"
        f"🔑 *Chave Pix:* `{CHAVE_PIX}`\n\n"
        "📸 Envie o comprovante aqui no chat para análise!"
    )

    context.user_data["plano_escolhido"] = nome_plano
    await query.message.reply_text(mensagem, parse_mode="Markdown")

async def receber_comprovante(update: Update, context: CallbackContext) -> None:
    """Recebe o comprovante, envia para o admin e armazena o usuário"""
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "Usuário desconhecido"
    
    # Armazena o usuário para aprovação posterior
    usuarios_pendentes[user_id] = (chat_id, context.user_data.get("plano_escolhido", "Desconhecido"))

    # Encaminha a foto para o admin com botão de aprovação
    photo = update.message.photo[-1].file_id
    caption = f"📌 *Novo pagamento recebido!*\n👤 Usuário: @{username}\n🆔 ID: `{user_id}`\n\nClique abaixo para aprovar. ✅"
    
    keyboard = [[InlineKeyboardButton("✅ Aprovar Pagamento", callback_data=f"aprovar_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
    await update.message.reply_text("📌 Comprovante enviado para análise. Aguarde a aprovação.")

async def aprovar_pagamento(update: Update, context: CallbackContext) -> None:
    """Aprova o pagamento e envia o link de acesso com um botão"""
    query = update.callback_query
    user_id = int(query.data.split("_")[1])

    # Apenas o admin pode aprovar
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Você não tem permissão para aprovar pagamentos.", show_alert=True)
        return

    if user_id in usuarios_pendentes:
        chat_id, plano = usuarios_pendentes.pop(user_id)
        
        # Adiciona a venda ao relatório
        if plano in relatorio_vendas:
            relatorio_vendas[plano] += 1

        # Criando um botão para acessar o grupo
        keyboard = [[InlineKeyboardButton("🔗 Entrar no Grupo VIP", url=LINK_ACESSO)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=chat_id, text="✅ *Pagamento aprovado!* Clique no botão abaixo para acessar o grupo VIP. 👇", parse_mode="Markdown", reply_markup=reply_markup)
        await query.edit_message_text("✅ Pagamento aprovado e acesso liberado!")

async def mostrar_vendas(update: Update, context: CallbackContext) -> None:
    """Mostra um relatório de vendas para o admin"""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Você não tem permissão para ver este relatório.")
        return

    mensagem = (
        "📊 *Relatório de Vendas*\n\n"
        f"💎 *7 dias:* {relatorio_vendas['7 dias']} vendas\n"
        f"💎 *15 dias:* {relatorio_vendas['15 dias']} vendas\n"
        f"💎 *30 dias:* {relatorio_vendas['30 dias']} vendas\n\n"
        "🔍 Total de vendas: *{}*".format(sum(relatorio_vendas.values()))
    )

    await update.message.reply_text(mensagem, parse_mode="Markdown")

async def erro(update: Update, context: CallbackContext) -> None:
    """Captura erros"""
    logging.error(f"Erro: {context.error}")

# Criar e rodar o bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(selecionar_plano, pattern="^plano_"))
    app.add_handler(MessageHandler(filters.PHOTO, receber_comprovante))
    app.add_handler(CallbackQueryHandler(aprovar_pagamento, pattern="^aprovar_"))
    app.add_handler(CommandHandler("vendas", mostrar_vendas))

    app.add_error_handler(erro)

    print("🚀 Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
