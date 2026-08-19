using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.ViewModels;

namespace web_app.Controllers;

public class DashboardController : Controller
{
    private readonly ApplicationDbContext _context;

    public DashboardController(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index(string searchString)
    {
        var totalJobs = await _context.Jobs.CountAsync();
        var totalTechnologies = await _context.Technologies.CountAsync();
        var totalCompanies = await _context.Companies.CountAsync();

        var topTechnologies = await _context.JobTechnologies
            .Include(jt => jt.Technology)
            .GroupBy(jt => jt.TechnologyId)
            .OrderByDescending(g => g.Count())
            .Take(10)
            .Select(g => new TopTechnologyItem
            {
                Name = g.First().Technology!.Name,
                Count = g.Count()
            })
            .ToListAsync();

        var model = new DashboardViewModel
        {
            TotalJobs = totalJobs,
            TotalTechnologies = totalTechnologies,
            TotalCompanies = totalCompanies,
            TopTechnologies = topTechnologies,
            SearchString = searchString
        };

        if (!string.IsNullOrWhiteSpace(searchString))
        {
            var term = searchString.Trim();
            model.SearchResults = await _context.Technologies
                .Where(t => t.Name != null && t.Name.ToUpper().Contains(term.ToUpper()))
                .OrderBy(t => t.Name)
                .Select(t => new TechnologySearchResult
                {
                    Id = t.Id,
                    Name = t.Name!
                })
                .ToListAsync();
        }

        return View(model);
    }
}
