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

    public async Task<IActionResult> Index(string? searchString)
    {
        var totalJobs = await _context.Jobs.CountAsync();
        var totalCompanies = await _context.Companies.CountAsync();

        var totalTechnologies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology")
            .Select(jk => jk.Keyword)
            .Distinct()
            .CountAsync();

        var topTechnologies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology")
            .GroupBy(jk => jk.Keyword)
            .OrderByDescending(g => g.Count())
            .Take(10)
            .Select(g => new TopTechnologyItem
            {
                Name = g.Key,
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
            model.SearchResults = await _context.JobKeywords
                .Where(jk => jk.Category == "technology" && jk.Keyword != null && jk.Keyword.ToUpper().Contains(term.ToUpper()))
                .Select(jk => jk.Keyword)
                .Distinct()
                .OrderBy(k => k)
                .Select(k => new TechnologySearchResult
                {
                    Name = k!
                })
                .ToListAsync();
        }

        return View(model);
    }
}
