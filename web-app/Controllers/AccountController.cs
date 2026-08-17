using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
namespace TechScope.Controllers;
using TechScope.Models;

/// <summary>
/// Controlador responsável pela gestão da autenticação e autorização de utilizadores.
/// Inclui as ações para registo, login e logout de utilizadores.
/// </summary>
public class AccountController : Controller
{
    // Gerenciador de utilizadores - permite criar, atualizar e eliminar utilizadores
    private readonly UserManager<ApplicationUser> _userManager;

    // Gerenciador de login - responsável pela autenticação e controlo de sessões
    private readonly SignInManager<ApplicationUser> _signInManager;

    /// <summary>
    /// Construtor do controlador que injeta as dependências necessárias.
    /// O ASP.NET Core fornece automaticamente estas instâncias através da Injeção de Dependências.
    /// </summary>
    /// <param name="userManager">Serviço para gerir utilizadores (criar, atualizar, eliminar)</param>
    /// <param name="signInManager">Serviço para gerir o login e autenticação</param>
    public AccountController(
        UserManager<ApplicationUser> userManager,
        SignInManager<ApplicationUser> signInManager)
    {
        _userManager = userManager;
        _signInManager = signInManager;
    }

    // ================= REGISTO DE UTILIZADORES =================

    /// <summary>
    /// Exibe o formulário de registo (GET).
    /// Este método responde aos pedidos GET para mostrar a página de registo.
    /// </summary>
    /// <returns>A vista do formulário de registo vazio</returns>
    [HttpGet]
    public IActionResult Register()
    {
        return View();
    }

    /// <summary>
    /// Processa o registo de um novo utilizador (POST).
    /// Este método:
    /// 1. Valida os dados do formulário
    /// 2. Cria um novo utilizador na base de dados
    /// 3. Faz login automático do utilizador
    /// 4. Redireciona para a página inicial ou volta ao formulário com erros
    /// </summary>
    /// <param name="model">Modelo contendo Email e Password do novo utilizador</param>
    /// <returns>Redireciona para Home/Index se sucesso, ou volta à vista com erros</returns>
    [HttpPost]
    public async Task<IActionResult> Register(RegisterViewModel model)
    {
        // Verifica se os dados enviados são válidos (email correto, passwords correspondidas, etc)
        if (!ModelState.IsValid)
            return View(model);

        var existingUser = await _userManager.FindByNameAsync(model.UserName);
        var existingEmail = await _userManager.FindByEmailAsync(model.Email);


        if (existingUser != null || existingEmail != null)
        {
            ModelState.AddModelError("", "Username or email already exist");
            return View(model);
        }

        // Cria um novo objeto de utilizador com o email como nome de utilizador
        var user = new ApplicationUser
        {
            UserName = model.UserName,
            Email = model.Email,
            FullName = model.FullName
        };

        // Tenta criar o utilizador com a password fornecida
        // O UserManager automaticamente encripta a password
        var result = await _userManager.CreateAsync(user, model.Password);

        // Se o registo foi bem-sucedido
        if (result.Succeeded)
        {
            // Faz login automático do utilizador (não precisa de fazer login manualmente)
            await _signInManager.SignInAsync(user, isPersistent: false);
            // Redireciona para o controller DashboardController e para a action Index
            return RedirectToAction();
        }

        // Se houve erros, adiciona-os ao ModelState para exibir no formulário
        foreach (var error in result.Errors)
            ModelState.AddModelError("", error.Description);

        // Volta a mostrar o formulário com os erros de validação
        return View(model);
    }

    // ================= LOGIN DE UTILIZADORES =================

    /// <summary>
    /// Exibe o formulário de login (GET).
    /// Este método responde aos pedidos GET para mostrar a página de login.
    /// </summary>
    /// <returns>A vista do formulário de login vazio</returns>
    [HttpGet]
    public IActionResult Login()
    {
        return View();
    }

    /// <summary>
    /// Processa o login de um utilizador (POST).
    /// Este método:
    /// 1. Valida os dados do formulário
    /// 2. Verifica as credenciais contra a base de dados
    /// 3. Se corretas, cria uma sessão autenticada
    /// 4. Se incorretas, exibe mensagem de erro
    /// </summary>
    /// <param name="model">Modelo contendo Email, Password e RememberMe do utilizador</param>
    /// <returns>Redireciona para Home/Index se sucesso, ou volta à vista com mensagem de erro</returns>
    [HttpPost]
    public async Task<IActionResult> Login(LoginViewModel model)
    {
        // Verifica se os dados enviados são válidos
        if (!ModelState.IsValid)
            return View(model);

        // Tenta fazer login com as credenciais fornecidas
        // - user.UserName: o username do utilizador (que acaba por ser o email mas o .net obriga a passar username)
        // - model.Password: a password do utilizador
        // - model.RememberMe: se true, mantém a sessão ativa após fechar o navegador
        // - lockoutOnFailure: se false, não bloqueia a conta após múltiplas tentativas falhadas

        // 1. Procurar utilizador pelo email
        var user = await _userManager.FindByEmailAsync(model.Email);

        if (user == null)
        {
            ModelState.AddModelError("", "Utilizador não encontrado");
            return View(model);
        }
        var result = await _signInManager.PasswordSignInAsync(
            user.UserName,//Fazer login usando o UserName (internamente obrigatório)
            model.Password,
            model.RememberMe,
            lockoutOnFailure: false);

        // Se o login foi bem-sucedido
        if (result.Succeeded)
            // Redireciona para a dashboard
            return RedirectToAction("Home");

        // Se as credenciais forem inválidas, exibe mensagem de erro
        ModelState.AddModelError("", "Credenciais inválidas");
        // Volta a mostrar o formulário com a mensagem de erro
        return View(model);
    }

    // ================= LOGOUT DE UTILIZADORES =================

    /// <summary>
    /// Faz logout do utilizador autenticado (GET).
    /// Este método:
    /// 1. Termina a sessão do utilizador
    /// 2. Remove a autenticação
    /// 3. Redireciona para a página inicial
    /// </summary>
    /// <returns>Redireciona para Home/Index após fazer logout</returns>
    public async Task<IActionResult> Logout()
    {
        // Termina a sessão atual do utilizador autenticado
        // Remove todos os cookies de autenticação
        await _signInManager.SignOutAsync();
        // Redireciona para a página inicial
        return RedirectToAction("Index", "Home");
    }
}