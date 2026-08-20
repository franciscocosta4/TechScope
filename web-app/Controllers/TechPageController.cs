using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.ViewModels;

namespace web_app.Controllers;

public class TechPageController : Controller
{
    private readonly ApplicationDbContext _context;

    public TechPageController(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index(int id)
    {
        var name = await _context.Technologies
            .Where(t => t.Id == id)
            .Select(t => t.Name)
            .FirstOrDefaultAsync();
            
        var jobs = await _context.JobTechnologies
            .Where(t => t.TechnologyId == id)
            .CountAsync();

        

        var model = new TechPageViewModel
        {
            TechId = id,
            Name = name,
            JobQuantity = jobs,
        };

        return View("~/Views/Dashboard/TechPage.cshtml", model);
    }
}
