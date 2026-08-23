using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.ViewModels;


namespace TechScope.Controllers;

public class JobsController : Controller
{

    private readonly ApplicationDbContext _context;

    public JobsController(ApplicationDbContext context)
    {
        _context = context;
    }


    public async Task<IActionResult> Index(string? searchString)
    {
        var totalJobs = await _context.Jobs.CountAsync();

        var model = new JobsViewModel
        {
            TotalJobs = totalJobs,
            SearchString = searchString
        };

        if (!string.IsNullOrWhiteSpace(searchString))
        {
            var term = searchString.Trim();

            model.ResultsCounter = _context.Jobs.Where(j => j.Title != null &&j.Title.ToUpper().Contains(term.ToUpper())).Count();
                
            model.SearchResults = await _context.Jobs
                .Where(j => j.Title != null &&
                            j.Title.ToUpper().Contains(term.ToUpper()))
                .Select(j => new JobsSearchResult
                {
                    Title = j.Title!,
                    ExternalId = j.ExternalId,
                    DatePosted = j.DatePosted,
                    CompanyName = j.Company.Name,
                })
                .Distinct()
                .OrderByDescending(x => x.DatePosted)
                .ToListAsync();
        }
        return View(model);
    }



}
