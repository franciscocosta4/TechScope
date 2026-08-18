using DotNetEnv;
using TechScope.Data;
using TechScope.Models;
using Microsoft.EntityFrameworkCore;

DotNetEnv.Env.Load("../.env");

var builder = WebApplication.CreateBuilder(args);

var connectionString =
    $"Host={Environment.GetEnvironmentVariable("PGHOST")};" +
    $"Port={Environment.GetEnvironmentVariable("PGPORT")};" +
    $"Database={Environment.GetEnvironmentVariable("PGDATABASE")};" +
    $"Username={Environment.GetEnvironmentVariable("PGUSER")};" +
    $"Password={Environment.GetEnvironmentVariable("PGPASSWORD")}";

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));


// Add services to the container.
builder.Services.AddControllersWithViews();

// Configurar Identity
builder.Services
    .AddDefaultIdentity<ApplicationUser>(options =>
    {
        // Comprimento mínimo da password.
        options.Password.RequiredLength = 4;

        // Não exige números.
        options.Password.RequireDigit = false;

        // Não exige letras minúsculas.
        options.Password.RequireLowercase = false;

        // Não exige letras maiúsculas.
        options.Password.RequireUppercase = false;

        // Não exige caracteres especiais.
        options.Password.RequireNonAlphanumeric = false;

        // Número mínimo de caracteres diferentes.
        options.Password.RequiredUniqueChars = 1;

        // Não exige confirmação de email.
        options.SignIn.RequireConfirmedAccount = false;
    })
    .AddEntityFrameworkStores<ApplicationDbContext>();

builder.Services.ConfigureApplicationCookie(options =>
{
    options.LoginPath = "/Account/Login";
    options.AccessDeniedPath = "/Account/AccessDenied";
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
