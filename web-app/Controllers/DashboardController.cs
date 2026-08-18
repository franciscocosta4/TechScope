using System.Diagnostics;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Identity;
using TechScope.Models;
using TechScope.Data;

namespace web_app.Controllers;


[Authorize]
public class DashboardController : Controller
{
    private readonly string _connectionString;

    private readonly ApplicationDbContext _context;
    private readonly UserManager<ApplicationUser> _userManager;
    public DashboardController(IConfiguration configuration, ApplicationDbContext context, UserManager<ApplicationUser> userManager)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")!;
        _context = context;
        _userManager = userManager;
    }


    public async Task<IActionResult> Index()
    {
        var user = await _userManager.GetUserAsync(User);
        // não precisa de ser assincrona pois nao vai a bd, apenas pega no id do User
        var userid = _userManager.GetUserId(User);

        var model = new DashboardViewModel
        {
            FullName = user.FullName,
            Email = user.Email,
            Initial = user.FullName?[0].ToString().ToUpper(),
        };

        return View(model);
    }


    // [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    // public IActionResult Error()
    // {
    //     return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    // }
}
